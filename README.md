# AI-Med-Conflict-Chatbot

## Project structure:


### Website


The main directory for the project with a web server/web page UI. To run from this level, type "python manage.py runserver" from the console, then access at 127.0.0.1:8000/bot in your browser.
Sub-directory /bot contains the files for the bot functionality, in config, corpora, interaction, rxnorm, and chatbot files. This is hooked up for Django implementation, and the surrounding files
are for the Django requirements. The web files are under /static/bot and /bot/templates. 

A live version is hosted at medbot-neural.net

### Corpora


Contains plaintext corpora from COCA, GloWbE, NOW, and Wikipedia, along with in-process web ripper code to build corpora.


### Nltk_data


Local install of NLTK_DATA with brown, conll2000, movie_reviews, and wordnet corpora, averaged_perception tagger, and punkt tokenizers.


### Nltk-3.3


Local install of National Language Toolkit 3.3


### Project


Chatbot experiment files, possible to run chatbot from console with files in this directory. Test functionality implemented. Note: not updated to latest server version.


### Resources


Any interesting or helpful documentation regarding NLP, AI/ML, etc

