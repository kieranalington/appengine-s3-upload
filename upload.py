import os
import base64
import hmac, sha
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

""" A simple file to generate a policy and signature to upload to S3 from appengine """


#DEFINE AWS CREDENTIALS
AWS_KEY = 'YOUR_AWS_KEY'
AWS_SECRET_KEY = 'YOUR_AWS_SECRET_KEY'

class MainPage(webapp.RequestHandler):
    
    def get(self):
        """ Take the request and create encoded values to allow file upload """
        
        file_name = 'file_name'
        
        return_url = 'http://localhost:8080'
        
        if not return_url:
            return self.response.out.write('Error: no return defined')
            
        #POLICY DOCUMENT - MUST BE STRING
        policy_document = '''{
          "expiration": "2015-06-15T12:00:00.000Z",
          "conditions": [
            {"bucket": "bucket-name" },
            ["starts-with", "$key", ""],
            ["starts-with", "$Content-Type", ""],
            {"acl": "public-read"},
            {"success_action_redirect": "%s"}
          ]
        }
        ''' % return_url
        
        #policy must be a base64 encoded version of the policy document
        policy = base64.b64encode(policy_document)
        
        #the signature is the policy + the AWS secret key
        signature = base64.b64encode(
            hmac.new(AWS_SECRET_KEY, policy, sha).digest())
                
        #template values to be passed through to upload.html
        template_values = {
                    'policy': policy,
                    'signature': signature,
                    'filename': file_name,
                    'return_url': return_url
                }
        
        #define the template
        path = os.path.join(os.path.dirname(__file__), 'upload.html')
        #write out
        self.response.out.write(template.render(path, template_values))

#only one URL route necessary
application = webapp.WSGIApplication(
                                     [('/', MainPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
