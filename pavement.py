import paver.doctools

options(
    sphinx=Bunch(
        docroot="docs",
        builddir="build",
        sourcedir="source"
    )
)

@task
@needs('paver.doctools.html')
def sphinx():
    """Build Sphinx documentation and install it into paver/docs"""
    builtdocs = path(options.sphinx.docroot) / options.sphinx.builddir / "html"
    destdir = path("dist") / "docs"
    destdir.rmtree()
    builtdocs.move(destdir)



@task
def epydoc():
    """ Build Epydoc documentation """
    from epydoc import cli
    options, names = cli.parse_arguments()
    options.target = path("dist") / "docs" / "api"
    options.target.rmtree()
    options.target.makedirs()

    cli.main(options, ['emergent'])
    
@task
@needs('epydoc')
@needs('sphinx')
def docs():
    """ Generate Sphinx and Epydoc documentation """
    
@task
def coverage():
    """ Generate test coverage report """
    import subprocess
    import os.path
    
    # Remove the *.pyc because sometimes coverage gets confused with old versions
    subprocess.call(['rm $(find . -name *.pyc)'], shell=True)

    nose_options = ['--with-coverage',
                    '--cover-package=emergent,emergent.test', 
                    '--cover-erase']

    coverage_results = path('dist') / 'test_coverage'

    coverage_options = ['-a', '-d', str(coverage_results)]

    # Extend coverage_options with the paths to emergent/*.py
    coverage_options.extend(
        str(filename) 
        for filename in path('emergent').walk()
        if os.path.splitext(str(filename))[1] == '.py'
    )

    subprocess.call(['nosetests'] + nose_options)

    coverage_results.rmtree()
    coverage_results.makedirs()
    subprocess.call(['coverage'] + coverage_options)







    
