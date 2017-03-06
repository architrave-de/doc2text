## Install Instructions

### Installation

1. Create a virtual environment. On a new terminal
window, run `mkvirtualenv -p python3.5 doc2text`
    
1. Activate the environment with `workon doc2text`
    
1. Install doc2text: `pip install
    git+ssh://git@github.com/architrave-de/doc2text.git`


### Running the command line tool.

If you already have activated the virtual environment, you just need
to execute the tool "doc2text". The name of the input file (the one
that contains the PDF and/or image you want) and the name of the
output (text) file that will be created.

There is an optional parameter to allow you to define what language to use.


`doc2text -i <YOUR INPUT FILE> -o <NAME OF TEXT FILE YOU WANT> -l < 3-letter code for language>`
