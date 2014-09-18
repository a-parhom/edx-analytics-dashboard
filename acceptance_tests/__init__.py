import os
from analyticsclient.client import Client

DASHBOARD_SERVER_URL = os.environ.get('DASHBOARD_SERVER_URL', 'http://127.0.0.1:9000')
DASHBOARD_FEEDBACK_EMAIL = os.environ.get('DASHBOARD_FEEDBACK_EMAIL', 'override.this.email@example.com')
USERNAME = os.environ.get('TEST_USERNAME', 'edx')
PASSWORD = os.environ.get('TEST_PASSWORD', 'edx')

# Determines if a second, scope authorization, page needs to be submitted/acknowledged
# after logging in at the OAuth provider.
ENABLE_OAUTH_AUTHORIZE = True

MAX_SUMMARY_POINT_VALUE_LENGTH = 13


class AnalyticsApiClientMixin(object):
    def setUp(self):
        super(AnalyticsApiClientMixin, self).setUp()

        api_url = os.environ.get('API_SERVER_URL', 'http://127.0.0.1:9001/api/v0')
        auth_token = os.environ.get('API_AUTH_TOKEN', 'edx')
        self.api_client = Client(api_url, auth_token=auth_token, timeout=5)


class FooterMixin(object):
    def test_footer(self):
        self.page.visit()

        # make sure we have the footer
        footer_selector = "footer[class=footer]"
        element = self.page.q(css=footer_selector)
        self.assertTrue(element.present)

        # check that we have an email
        selector = footer_selector + " a[class=feedback-email]"
        element = self.page.q(css=selector)
        self.assertEqual(element.text[0], DASHBOARD_FEEDBACK_EMAIL)

        # Verify the terms of service link is present
        selector = footer_selector + " a[data-role=tos]"
        element = self.page.q(css=selector)
        self.assertTrue(element.present)
        self.assertEqual(element.text[0], u'Terms of Service')

        # Verify the privacy policy link is present
        selector = footer_selector + " a[data-role=privacy-policy]"
        element = self.page.q(css=selector)
        self.assertTrue(element.present)
        self.assertEqual(element.text[0], u'Privacy Policy')


class CoursePageTestsMixin(object):
    """
    Convenience methods for testing.
    """

    def assertValidHref(self, selector):
        element = self.page.q(css=selector)
        self.assertTrue(element.present)
        self.assertNotEqual(element.attrs('href')[0], '#')

    def assertTableColumnHeadingsEqual(self, table_selector, headings):
        rows = self.page.q(css=('%s thead th' % table_selector))
        self.assertTrue(rows.present)
        self.assertListEqual(rows.text, headings)

    def assertElementHasContent(self, css):
        element = self.page.q(css=css)
        self.assertTrue(element.present)
        html = element.html[0]
        self.assertIsNotNone(html)
        self.assertNotEqual(html, '')

    def assertSummaryPointValueEquals(self, data_selector, value):
        """
        Compares the value in the summary card the "value" argument.

        Arguments:
            data_selector (String): Attribute selector (ex. data-stat-type=current_enrollment)
            tip_text (String): expected value
        """
        # Account for Django truncation
        value = (value[:(MAX_SUMMARY_POINT_VALUE_LENGTH - 3)] + '...') if len(
            value) > MAX_SUMMARY_POINT_VALUE_LENGTH else value

        element = self.page.q(css="div[{0}] .summary-point-number".format(data_selector))
        self.assertTrue(element.present)
        self.assertEqual(element.text[0], value)

    def assertSummaryTooltipEquals(self, data_selector, tip_text):
        """
        Compares the tooltip in the summary card the "tip_text" argument.

        Arguments:
            data_selector (String): Attribute selector (ex. data-stat-type=current_enrollment)
            tip_text (String): expected text
        """
        help_selector = "div[{0}] .summary-point-help".format(data_selector)
        element = self.page.q(css=help_selector)
        self.assertTrue(element.present)

        # check to see if
        screen_reader_element = self.page.q(css=help_selector + " > span[class=sr-only]")
        self.assertTrue(screen_reader_element.present)
        self.assertEqual(screen_reader_element.text[0], tip_text)

        tooltip_element = self.page.q(css=help_selector + " > i[data-toggle='tooltip']")
        self.assertTrue(tooltip_element.present)
        # the context of title gets move to "data-original-title"
        self.assertEqual(tooltip_element[0].get_attribute('data-original-title'), tip_text)


def auto_auth(browser, server_url):
    url = '{}/test/auto_auth/'.format(server_url)
    return browser.get(url)
