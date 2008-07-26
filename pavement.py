import paver.doctools

options(
    setup=Bunch(
        name='Emergent',
        version='1.1',
        description='A humble attempt at creating emergent behavior',
        author='Carlo Cabanilla',
        author_email='carlo.cabanilla@gmail.com',
        url='http://syntacticbayleaves.com',
        packages=['emergent'],
        scripts=['bin/emergent'],
        test_suite='nose.collector',
    ),
    
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
    
    
    