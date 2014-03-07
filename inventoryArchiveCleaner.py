# dropbox archive cleaner

import ConfigParser
import os
import io
import dropbox
from datetime import *

config = ConfigParser.ConfigParser(allow_no_value=True)
configFilePath = 'c:\\Users\\andys\\Dropbox\\shopify\\inventory.config'
if not os.path.isfile(configFilePath):
    print "config file " + configFilePath + " not found"
    exit()

config.read(configFilePath)

# get the app key and secret from the config file
dropbox_app_key = config.get('dropbox','dropbox_app_key')
dropbox_app_secret = config.get('dropbox','dropbox_app_secret')
## if there is no access token then prompt for access granting
dropbox_access_token = config.get('dropbox','dropbox_access_token')

archive_path = config.get('FileSection','archive_path')
max_age = config.get('FileSection','max_age')

if not dropbox_access_token:
    print "no dropbox token found"
    flow = dropbox.client.DropboxOAuth2FlowNoRedirect(dropbox_app_key, dropbox_app_secret)
    authorize_url = flow.start()
    print '******'
    print 'Now I will open a dropbox web page in your web browser.'
    print 'Click "Allow" on that page (you might have to log in first)'
    print 'Copy the authorization code.'
    print 'Return here once you have copied it to the clipboard'
    tmp=raw_input("--->push Enter when ready...")
    webbrowser.open(authorize_url)
    print 'right-click to paste'
    code = raw_input("paste the authorization code here: ").strip()
    # This will fail if the user enters an invalid authorization code
    dropbox_access_token, dropbox_user_id = flow.finish(code)
    
    cfgfile = open(configFilePath,'w')
    
    config.set('dropbox','dropbox_user_id',dropbox_user_id)
    config.set('dropbox','dropbox_access_token',dropbox_access_token)
    config.write(cfgfile)
    cfgfile.close()
    print "access token received and saved"
    
# found the access_token either in the config or from the above auth action
client = dropbox.client.DropboxClient(dropbox_access_token)
print 'connected to dropbox'
print 'linked account name: ', client.account_info()["display_name"]
print 'linked account email: ', client.account_info()["email"]
print

folder_metadata = client.metadata(archive_path)
for file_meta in folder_metadata['contents']:
    #print file_meta['path']
    #print file_meta['modified']
    #Tue, 31 Dec 2013 20:55:22 +0000
    file_date = datetime.strptime(file_meta['modified'], "%a, %d %b %Y %H:%M:%S +0000")
    if not file_date < (datetime.now()-timedelta(days=int(max_age))):
        print "keeper " + file_meta['path']
    else:
        print "deleting " + file_meta['path']
        print file_meta['modified']
        client.file_delete(file_meta['path'])
    