module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    htmllint: {
      options: {
        ignore: 'Attribute “color” not allowed on element “link” at this point.',
        errorlevels: 'error',
        force: true,
      },
      lint: ["_site/**/*.html", "!_site/zohoverify/*", "!_site/google*", "!_site/verslag/index.html"]
    },
    bootlint: {
      options: {
        stoponerror: false,
        relaxerror: ['W005']
      },
      lint: ["_site/**/*.html", "!_site/zohoverify/*", "!_site/google*"]
    },
    uglify: {
        options: {
          preserveComments: 'some',
        },
        build: {
          files: {
          'scripts/site.min.js': ['_scripts/libs/jquery-1.12.4.js', '_scripts/libs/bootstrap-3.3.7.js', '_scripts/libs/bootstrap-accessibility-1.0.3.js', '_scripts/components/footer.js'],
          'scripts/homepage.min.js': ['_scripts/components/home/decrypt.js', '_scripts/components/home/scrolling.js', '_scripts/components/home/google-maps.js'],
          'scripts/post.min.js': ['_scripts/libs/chessboard-0.3.0_mod.js', '_scripts/libs/chessboardjs-themes.js', '_scripts/components/chessboard/show-solution.js'],
          }
        }
    },
    jshint: {
      lint: ['Gruntfile.js', '_site/scripts/homepage.js', '_site/scripts/lib/chessboard-0.3.0_orig.js', '_site/scripts/componenten/footer.js']
    },
  });
  // src: ['_site/scripts/site.js', '_site/scripts/homepage.js', '_site/scripts/post.js'],
  // dest: ['scripts/site.min.js', 'scripts/homepage.min.js', 'scripts/post.min.js']

  // Load the plugin that provides the "uglify" task.
  grunt.loadNpmTasks('grunt-html');
  grunt.loadNpmTasks('grunt-bootlint');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-jshint');

  // Default task(s).
  grunt.registerTask('default', ['uglify', 'htmllint', 'bootlint', 'jshint']);
  grunt.registerTask('lint', ['htmllint:lint', 'bootlint:lint', 'jshint:lint']);
  grunt.registerTask('build', ['uglify:build']);
};
