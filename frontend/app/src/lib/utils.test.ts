import { test, expect } from 'vitest';
import { example_test } from './utils';

test('example test', () => {
	const test_string = "string"
	const expected_string = "example_string"
	expect(example_test(test_string)).toBe(expected_string);
});
