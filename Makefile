
install: build
	python setup.py install --prefix ~/research/pekb/pdkb-planning

build: 
	python setup.py build

test: install
	python bin/test.py test test_all

run: install
	python -O bin/belief_change.py run

assess: aamas.csv install
	python bin/belief_change.py assess 
