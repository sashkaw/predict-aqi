const path = require("path");
//const webpack = require("webpack");
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  entry: "./src/index.js",
  output: {
    path: path.resolve(__dirname, "./static/frontend"),
    filename: "[name].js",
  },
  resolve: {
    extensions: ['', '.js', '.jsx'],
  },
  module: {
    rules: [
      {
        //test: /\.js$/,
        test: /\.js$|jsx/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
        },
      },
      {
        test: /\.css$/i,
        use: ['style-loader', 'css-loader'],
      },
    ],
  },
  optimization: {
    minimize: true,
  },
  plugins: [
      new HtmlWebpackPlugin({
        template: "./templates/frontend/index.html",
        filename: "./index.html",
        // This has effect on the react lib size
        "process.env.NODE_ENV": JSON.stringify("production"),
        //"process.env.NODE_ENV": JSON.stringify("development"), // must match what is in package.json
    }),
    /*new webpack.DefinePlugin({
      // This has effect on the react lib size
      //"process.env.NODE_ENV": JSON.stringify("production"),
      "process.env.NODE_ENV": JSON.stringify("development"), // must match what is in package.json
    }),*/
  ],
};