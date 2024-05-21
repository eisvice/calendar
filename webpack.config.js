const path = require('path');
const webpack = require('webpack');
const plugin = require('tailwindcss');


module.exports = {
    entry: {
        bundle: './assets/scripts/index.js'
    },
    output: {
        filename: '[name].js',
        path: path.resolve(__dirname, 'mnts', 'static')
    },
    module: {
        rules: [
            {
                test: /\.css$/i,
                use: [
                    'style-loader',
                    'css-loader'
                ]
            }
        ]
    },
    plugins: [
        // load `moment/locale/ru.js`
        new webpack.ContextReplacementPlugin(/moment[/\\]locale$/, /ru/),
      ],
};