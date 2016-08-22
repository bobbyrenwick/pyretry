import unittest

import mock

from .pyretry import retry


class RetryableError(Exception):
    pass


class DifferentRetryableError(Exception):
    pass


class UnretryableError(Exception):
    pass


class TestPyretry(unittest.TestCase):

    def setUp(self):
        self.counter = 0

    def test_none_failing_function(self):

        @retry(RetryableError)
        def no_errors():
            self.counter += 1
            return 'succeeded'

        r = no_errors()

        self.assertEqual(r, 'succeeded')
        self.assertEqual(self.counter, 1)

    def test_retries_once(self):
        @retry(RetryableError)
        def fails_once():
            self.counter += 1

            if self.counter == 1:
                raise RetryableError
            else:
                return 'succeeded'

        r = fails_once()
        self.assertEqual(r, 'succeeded')
        self.assertEqual(self.counter, 2)

    def test_limit_is_reached(self):
        @retry(RetryableError, num_retries=5)
        def always_fails():
            self.counter += 1
            raise RetryableError

        self.assertRaises(RetryableError, always_fails)
        self.assertEqual(self.counter, 6)

    def test_other_exception_not_caught(self):
        @retry(RetryableError)
        def raises_unretryable():
            self.counter += 1
            raise UnretryableError

        self.assertRaises(UnretryableError, raises_unretryable)
        self.assertEqual(self.counter, 1)

    def test_multiple_exception(self):
        @retry((RetryableError, DifferentRetryableError))
        def raises_multiple_exceptions():
            self.counter += 1

            if self.counter == 1:
                raise RetryableError
            if self.counter == 2:
                raise DifferentRetryableError
            if self.counter == 3:
                return 'succeeded'

        r = raises_multiple_exceptions()
        self.assertEqual(r, 'succeeded')
        self.assertEqual(self.counter, 3)

    def test_timeout_as_float(self):
        @retry(RetryableError, timeout=0.1)
        def fails_twice():
            self.counter += 1

            if self.counter == 3:
                return 'succeeded'
            else:
                raise RetryableError

        r = fails_twice()
        self.assertEqual(r, 'succeeded')
        self.assertEqual(self.counter, 3)

    def test_timeout_as_function(self):
        def side_effect(retry_number):
            return retry_number / 100.0

        timeout_calc = mock.MagicMock()
        timeout_calc.side_effect = side_effect

        @retry(RetryableError, num_retries=5, timeout=timeout_calc)
        def always_fails():
            self.counter += 1
            raise RetryableError

        self.assertRaises(RetryableError, always_fails)
        self.assertEqual(self.counter, 6)

        expected = [mock.call(i + 1) for i in range(5)]
        self.assertEqual(timeout_calc.call_args_list, expected)

    def test_hook_is_called(self):
        hook = mock.MagicMock()
        timeout = 0.1

        @retry(RetryableError, num_retries=5, timeout=timeout, hook=hook)
        def always_fails():
            self.counter += 1
            raise RetryableError

        self.assertRaises(RetryableError, always_fails)
        self.assertEqual(self.counter, 6)

        for i, call in enumerate(hook.call_args_list):
            self.assertTrue(isinstance(call[0][0], RetryableError))
            self.assertEqual(call[0][1], i + 1)
            self.assertEqual(call[0][2], timeout)
