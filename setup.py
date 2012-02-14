from distutils.core import setup

setup(

	name="maptools",
	version ="0.0.4",
        author="Privezentsev Konstantin",
	author_email = "privezentsev@gmail.com",
        
	packages = ["maptools"],
        package_dir={'maptools':'maptools'},
	package_data={'maptools': ['data/*']},
	scripts = ["addminimap","splitmap","crop4paper.py","topomerge.py","topomerge-win.py"]    	
    
)

