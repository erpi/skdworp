module.exports = function(grunt) {
  var navbar = ['.fade', '.fade.in', '.collapse', '.collapse.in', '.collapsing', '.alert-danger', /\.open/, /\.navbar-nav.+\.active/];
  var navchess = navbar.concat([/\.clearfix/, /\.board/, /\.square/, /\.white/, /\.black/, /\.highlight/, /\.notation/, /\.alpha/, /\.numeric/]);
  var navchessimg = navchess.concat(['.img-responsive', '.center-block'])
  var navblitz = navbar.concat([".doorstreept", ".grijs"])

  require('load-grunt-tasks')(grunt);
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
              'scripts/site.min.js': ['_scripts/libs/jquery-1.12.4.js', '_scripts/components/home/decrypt.js', '_scripts/libs/bootstrap-3.3.7.js', '_scripts/components/footer.js', '_scripts/components/verslag-schrijven.js', '_scripts/components/verslag.js', '_scripts/components/snelschaak.js', '_scripts/components/tussenstand.js', '_scripts/components/open.js'],
              'scripts/homepage.min.js': ['_scripts/components/home/scrolling.js', '_scripts/libs/leaflet-1.3.4.js', '_scripts/components/home/openstreetmap.js'],
          'scripts/post.min.js': ['_scripts/libs/chessboard-0.3.0_mod.js', '_scripts/libs/chessboardjs-themes.js', '_scripts/components/chessboard/show-solution.js'],
          }
        }
    },
    jshint: {
      lint: ['Gruntfile.js', '_scripts/**/*.js', '_scripts/libs/chessboardjs-themes.js']
    },
    // verwijder alles in de build directory
    clean: {
      options: {
        'no-write': false
      },
      build: ['<%= builddir %>'],
    },
    copy: {
      // kopieer nodige sass-hoofdbestanden naar build-directory
      build1: {
        files: [{
          expand: true,
          nonull: true,
          cwd: '<%= sassdir %>',
          src: ['_site.scss', '_homepage.scss', '_post.scss', 'componenten/_chessboard-0.3.0.scss'],
          dest: '<%= builddir %>',
          flatten: true,
          // verwijder underscores en andere rommel uit de bestandsnamen
          rename:  function (dest, src) {
            s = src.replace(/[^A-Za-z.]/g, '');
            return dest + s.replace(/\.+/g, '.');
          }
        }]
      },
      // kopieer gegenereerde min.css bestanden naar directory met css styles voor jekyll
      build2: {
        files: [{
          expand: true,
          nonull: true,
          cwd: '<%= builddir %>',
          src: ['*.min.css', '!homepage*'],
          dest: '<%= styledir %>',
        },
        // kopieer inline css voor homepage naar _include directory van jekyll
        {
          expand: true,
          nonull: true,
          cwd: '<%= builddir %>',
          src: 'homepage.min.css',
          dest: '<%= includedir %>',
        }]
      },
    },
    // bouw css-bestanden met behulp van libsass
    sass: {
      options: {
        includePaths: ['<%= sassdir %>'],
      },
      build: {
        files: [{
          nonull: true,
          expand: true,
          cwd: '<%= builddir %>',
          src: ['*.scss'],
          dest: '<%= builddir %>',
          ext: '.css',
        }],
      }
    },
    // strip overbodige css met behulp van uncss
    // http://stackoverflow.com/questions/28082782/gulp-uncss-breaks-bootstrap-dropdown-navbar-navigation
    uncss: {
      options: {
        ignore: '<%= navblitz %>',
      },
      buildsite: {
        options: {
          stylesheets: ['../<%= builddir %>site.css'],
        },
        files: {
          '<%= builddir %>site.un.css': ['<%= allpages %>', '!<%= homepage %>', '!<%= postpages %>'],
        }
      },
      buildhomepage: {
        options: {
          stylesheets: ['../<%= builddir %>homepage.css'],
        },
        files: {
          '<%= builddir %>homepage.un.css': ['<%= homepage %>'],
        }
      },
      buildpost: {
        options: {
          ignore: '<%= navchessimg %>',
          stylesheets: ['../../../../<%= builddir %>post.css', '../../../../<%= builddir %>chessboard.css'],
        },
        files: {
          '<%= builddir %>post.un.css': ['<%= postpages %>'],
        }
      },
    },
    //
    cssmin: {
      options: {
        compatibility: 'ie8',
        keepSpecialComments: 0,
        report: 'gzip',
      },
      build: {
        files: [{
          nonull: true,
          expand: true,
          cwd: '<%= builddir %>',
          src: ['*.un.css'],
          dest: '<%= builddir %>',
          ext: '.min.css',
        }]
      }
    },

    sassdir: '_sass/',
    builddir: 'build-grunt/',
    jekyllbuilddir: '_site/',
    styledir: 'styles/',
    includedir: '_includes/',
    navbar: navbar,
    navchess: navchess,
    navchessimg: navchessimg,
    navblitz: navblitz,
    allpages: '<%= jekyllbuilddir %>**/*.html',
    homepage: '<%= jekyllbuilddir %>index.html',
    postpages: '<%= jekyllbuilddir %>20*/**/*.html',

  });

  // Task(s).
  grunt.registerTask('build-uncss', ['uncss:buildsite', 'uncss:buildhomepage', 'uncss:buildpost']);
  grunt.registerTask('build-css', ['clean:build', 'copy:build1', 'sass:build', 'build-uncss', 'cssmin:build', 'copy:build2']);
  grunt.registerTask('lint', ['htmllint:lint', 'bootlint:lint', 'jshint:lint']);
  grunt.registerTask('build', ['uglify:build', 'build-css']);
  grunt.registerTask('default', ['uglify', 'htmllint', 'bootlint', 'jshint']);
};
