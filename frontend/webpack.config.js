const path = require("path");

module.exports = (env, argv) => ({
  entry: "./src/management.js",
  output: {
    path: path.resolve(__dirname, "dist"),
    filename: "management.js",
  },
  module: {
    rules: [
      {
        test: /\.m?js$/,
        exclude: /node_modules/,
        include: path.resolve(__dirname, "src"),
        use: {
          loader: "babel-loader",
          options: {
            presets: ["@babel/preset-react"],
          },
        },
      },
    ],
  },
  devtool: argv.mode === "development" ? "eval-source-map" : undefined,
});
