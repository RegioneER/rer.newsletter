process.traceDeprecation = true;
const mf_config = require('@patternslib/dev/webpack/webpack.mf');
const path = require('path');
const package_json = require('./package.json');
const package_json_mockup = require('@plone/mockup/package.json');
const package_json_patternslib = require('@patternslib/patternslib/package.json');
const webpack_config =
  require('@patternslib/dev/webpack/webpack.config').config;

module.exports = () => {
  let config = {
    entry: {
      'manageusers.min': path.resolve(
        __dirname,
        'src/rer/newsletter/browser/static/scripts/index_manageusers',
      ),
      'channelhistory.min': path.resolve(
        __dirname,
        'src/rer/newsletter/browser/static/scripts/index_channelhistory',
      ),
      'initializedModal.min': path.resolve(
        __dirname,
        'src/rer/newsletter/browser/static/scripts/index_initializedModal',
      ),
    },
  };

  config = webpack_config({
    config: config,
    package_json: package_json,
  });
  config.output.path = path.resolve(
    __dirname,
    'src/rer/newsletter/browser/static/scripts/prod',
  );

  config.module.rules.push({
    test: /\.svg$/i,
    type: 'asset/resource',
  });

  config.plugins.push(
    mf_config({
      name: 'rer.newsletter',
      filename: 'bundle-remote.min.js',
      remote_entry: config.entry['manageusers.min'],
      dependencies: {
        ...package_json_patternslib.dependencies,
        ...package_json_mockup.dependencies,
        ...package_json.dependencies,
      },
    }),
  );

  if (process.env.NODE_ENV === 'development') {
    config.devServer.port = '3001';
    config.devServer.static.directory = path.resolve(__dirname, './resources/');
  }

  // console.log(JSON.stringify(config, null, 4));

  return config;
};
