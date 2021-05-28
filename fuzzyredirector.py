import pandas as pd, PySimpleGUI as sg, re, fuzzy
from fuzzywuzzy import process
from urllib.parse import urlparse

def main():
    # default values
    source = 'src.csv'
    destination = 'dst.csv'
    mode = 'lastpath'
    querystring = False

    # Make input gui window
    layout = [
        [sg.Text("Choose source file: "), sg.Input(source), sg.FileBrowse()],
        [sg.Text("Choose destination file: "), sg.Input(destination), sg.FileBrowse()],
        [sg.Text("Select match mode: ")],
        [sg.Radio('Lastpath match', "mode", default=True)],
        [sg.Radio('Reverse match', "mode", default=False)],
        [sg.Radio('Full Path', "mode", default=False)],
        [sg.Radio('Soundex dude!', "mode", default=False)],

        [sg.Text("Include querystrings?")],
        [sg.Radio('Aye', "strings", default=False)],
        
        [sg.Button("Submit")]
              ]
    window = sg.Window("Demo", layout)
    [sg.FileBrowse()]
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event=="Exit":
            break
        elif event == "Submit":
            if values[0] != '':
                source = values[0]
            if values[1] != '':
                destination = values[1]
            if values[3]:
                mode = 'reverse'
            elif values[4]:
                mode = 'full'
            elif values[5]:
                mode = 'soundex'
            querystring = values[6]
            break
    window.close()
   
    src = pd.read_csv(source, dtype='unicode').fillna('')
    src['String'] = src['URL'].apply(stringify, args=(mode, querystring,))
    
    dst = pd.read_csv(destination, dtype='unicode').fillna('')
    dst['String'] = dst['URL'].apply(stringify, args=(mode, querystring,))

    ## match
    match = src['String'].apply(fuzzify, args=(dst,))
    src = src.merge(match, left_on='String', right_on='String')
    src.to_csv('mapped.csv', mode='w' ,encoding='utf-8-sig')

def stringify(url, mode, querystring):
    u = urlparse(url)
    if mode == 'lastpath':
        url = u.path.strip('/').split('/')[-1]
        if querystring:
           url += ''.join([u.params,u.query,u.fragment])
    
    elif mode == 'reverse':
        url = u.path[1:].split('/')[::-1]
        if querystring:
           url.extend([u.params,u.query,u.fragment])
        url = ' '.join(url).strip()    

    elif mode == 'full':
        url = u.path
        if querystring:
           url += ''.join([u.params,u.query,u.fragment])
    elif mode == 'soundex':
        soundex = fuzzy.Soundex(4)
        url = u.path.strip('/').split('/')[-1]
        if querystring:
           url += ''.join([u.params,u.query,u.fragment])
        url = soundex(url)

    return re.sub('[^0-9a-zA-Z]+', ' ', url).strip()

def fuzzify(string, dst):
    result = process.extractOne(string, dst['String'].values.tolist())
    choices = string
    data = dst.loc[dst['String'] == result[0]].values[0][0]
    match = result[1]
    return pd.Series([choices,data,match],index=['String','Destination','Ratio'])

if __name__ == "__main__":
    main()
