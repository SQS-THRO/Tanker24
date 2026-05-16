//this require needs to be ignored by eslint because webpack needs it to be commonjs
// eslint-disable-next-line @typescript-eslint/no-require-imports
const path = require('path');

module.exports = {
	resolve: {
		alias: {
			$lib: path.resolve(__dirname, 'src/lib')
		}
	}
};
