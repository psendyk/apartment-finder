# apartment-finder
## Dependencies
- [`python-craigslist`](https://github.com/juliomalegria/python-craigslist)
- [`requests`](https://pypi.org/project/requests/)
- `python >= 3.5.0`
The above dependencies can be installed by running `pip3 install -r requirements.txt` in the cloned repo directory.
## Usage
You can simply run the script by typing `python3 apartment_finder.py` inside the cloned repo. The present Procfile can be used for deployment on an external server(e.g. you can run it on Heroku using `heroku run apartment_finder.py`).  
The exisiting `config.json` file can (and should) be modified to match your preferences.  
- `city`, `craigslist_site`, `craigslist_area`: please refer to [Craigslist](https://craigslist.org/) for your city codes
- `bounding_boxes`: a dictonary mapping neighborhood names to their bounding boxes coordinates, please refer to the sample `config.json` for the correct structure.
- `from_email`, `password`: your email credentials
- `to_email`: a list of destination emails
- `run_interval`: how often the script should be run in minutes (default is 20)
