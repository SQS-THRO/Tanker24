const path = require('path');

module.exports = {
    resolve: {
        alias: {
            $lib: path.resolve(__dirname, 'src/lib')
        }
    }
};
