const path = require('path');

module.exports = {
	mode: process.env.NODE_ENV === 'production' ? 'production' : 'development',
	entry: ['./src/scss/styles.scss', './src/scripts/scripts.js'],
	output: {
		path: path.resolve(__dirname, 'flask_server/static'),
		filename: 'js/scripts.js',
	},
	module: {
		rules: [
			{
				test: /\.scss$/,
				use: [
					{
						loader: 'file-loader',
						options: {
							name: 'css/[name].css',
						}
					},
					{
						loader: 'extract-loader'
					},
					{
						loader: 'css-loader?-url'
					},
					{
						loader: 'postcss-loader'
					},
					{
						loader: 'sass-loader'
					}
				]
			}
		]
	}
};