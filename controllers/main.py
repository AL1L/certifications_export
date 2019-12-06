# -*- coding: utf-8 -*-

from datetime import datetime
import base64
import json
import csv
import io
from dateutil.relativedelta import relativedelta

from odoo import http, _
from odoo.exceptions import UserError
from odoo.http import request, content_disposition


class Test(http.Controller):
    @http.route(['/firefly_test/test'], type='json', auth='user', methods=['GET'], website=True)
    def test(self, fields):
        return {
            'foo': 'bar'
        }


class FireflyExport(http.Controller):

    @http.route(['/firefly/export'], type='http', auth='user', methods=['GET'], website=True)
    def csv_download(self, **kw):
        search = []
        certs = []
        if 'certs' in kw:
            certs = kw.get('certs').split(',')

        if len(certs) > 0:
            search.append(('id', 'in', certs))

        surveys = http.request.env['survey.survey'].search_read(search, [
            'title'])

        if len(surveys) == 0:
            raise UserError(_("No surveys not found"))

        csv = self.generate_cert_report(cert_filter=search)

        if len(certs) == 1:
            survey = surveys[0]
            filename = 'Certification Report - {} - {}.csv'.format(
                survey['title'], datetime.now().strftime("%m-%d-%Y"))
        else:
            filename = 'Certification Report - {}.csv'.format(
                datetime.now().strftime("%m-%d-%Y"))

        headers = [
            ('Content-Type', 'application/octet-stream'),
            ('Content-Disposition', 'attachment; filename="%s"' % (filename))
        ]

        return request.make_response(csv, headers=headers)

    def generate_cert_report(self, cert_filter=[], user_filter=[]):
        cert_filter.append(("certificate", "=", True))
        certifications = http.request.env['survey.survey'].search_read(
            cert_filter, [])

        cert_ids = []

        for cert in certifications:
            cert_ids.append(cert["id"])
            cert["answers"] = {}

        certification_answers = http.request.env['survey.user_input'].search_read([("test_entry", "=", False)], [
            "survey_id", "create_date", "deadline", "partner_id", "email", "input_type", "attempt_number", "state", "test_entry", "quizz_passed", "quizz_score", "__last_update"])

        csv_data = [
            ['', ''],
            ['', ''],
        ]
        user_rows = {}

        for answer in certification_answers:
            if not answer["partner_id"]:
                continue
            user_id = answer["partner_id"][0]

            for cert in certifications:
                if cert["id"] != answer["survey_id"][0]:
                    continue

                if user_id in cert["answers"]:
                    if answer["attempt_number"] <= cert["answers"][user_id]["attempt_number"]:
                        break

                cert["answers"][user_id] = answer

            # TODO: Add sorting
            if user_id not in user_rows:
                user_rows[user_id] = [answer["partner_id"][1], '']

        user_rows["filler"] = ['', '']
        user_rows["averages"] = ['', '']

        for cert in certifications:
            csv_data[0].extend(['', cert['title'], '', '', ''])
            csv_data[1].extend(
                ['', 'Date Assigned', 'Date Completed', 'Next Due Date', 'Score'])

            score_sum = 0
            score_count = 0

            for user_id in user_rows:
                if isinstance(user_id, str):
                    continue

                user_row = user_rows[user_id]

                if user_id in cert["answers"]:
                    answer = cert["answers"][user_id]

                    started = answer["create_date"]
                    completed = None
                    expires = None
                    score = None

                    if answer["state"] == "done":
                        completed = answer["__last_update"]
                        score = f"{answer['quizz_score']:.2f}%"
                        expires = "n/a"

                        score_sum += answer['quizz_score']
                        score_count += 1

                        if "x_expires" in cert and cert["x_expires"] != 0:
                            expires = completed + \
                                relativedelta(months=+cert["x_expires"])

                        # Formatting
                        if isinstance(completed, datetime):
                            completed = completed.strftime("%m/%d/%Y")
                        if isinstance(expires, datetime):
                            expires = expires.strftime("%m/%d/%Y")
                    else:
                        completed = "Incomplete"
                        expires = "Incomplete"
                        score = "Incomplete"

                    user_row.extend(
                        ['', started.strftime("%m/%d/%Y"), completed, expires, score])
                else:
                    user_row.extend(['', '', '', '', ''])

            average_score = "n/a"

            if score_count > 0:
                average_score = f"{score_sum / score_count:.2f}%"

            user_rows["averages"].extend(
                ['', '', '', 'Average:', average_score])

        output = self.create_csv(csv_data, user_rows=user_rows)

        return output

    def create_csv(self, l, user_rows=None):
        csv_data = list(l)
        if user_rows is not None:
            for user_id in user_rows:
                user_row = user_rows[user_id]

                csv_data.append(user_row)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(csv_data)

        return output.getvalue()
