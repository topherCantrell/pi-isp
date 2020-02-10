import os

import tornado.ioloop
import tornado.web

TESTING = True

if TESTING:
    # WINDOWS HACK
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # python-3.8.0a4
    ISP = None
else:
    import isp8051
    ISP = isp8051.ISP8051()


class UploadHandler(tornado.web.RequestHandler):
    def post(self):
        start_address = self.get_argument('start', '0')
        base = 10
        if start_address.startswith('0x'):
            base = 16
            start_address = int(start_address,base)
        bin_data = self.request.files['binfile'][0]['body']        
        
        print('##',start_address,bin_data)
        
        #extension = os.path.splitext(original_fname)[1]
        #fname = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(6))
        #final_filename= fname+extension
        #output_file = open("uploads/" + final_filename, 'w')
        #output_file.write(file1['body'])
        
        self.finish("file is uploaded")

class ISPHandler(tornado.web.RequestHandler):
    
    def get(self):
        start_address = int(self.get_argument('start', '0'))
        num_bytes = int(self.get_argument('size', '256'))
            
        if ISP:               
            ISP.set_reset(True)   
            ISP.enable_programming()
            data = ISP.read_bytes(start_address,num_bytes)
            ISP.set_reset(False)
        else:
            data = [45]*num_bytes         
        
        ret = {
            'start' : start_address,
            'size' : num_bytes,
            'data' : data
            }        
        
        self.set_header('Content-Type', 'application/json')
        self.write(ret)
        
    def patch(self):        
        '''        
        {
            'start' : 0,
            'data' : [1,2,3,4]
        }        
        '''
        
        req = tornado.escape.json_decode(self.request.body)
                
        if ISP:
            ISP.set_reset(True) 
            ISP.enable_programming()
            ISP.erase()
            ISP.write_bytes(req['start'],req['data'])
            ISP.set_reset(False)
        else:
            pass
        
        ret = {
            'start' : req['start'],
            'size' : len(req['data'])
        }        
        
        self.set_header('Content-Type', 'application/json')
        self.write(ret)
            
if __name__ == '__main__': 
            
    root = os.path.join(os.path.dirname(__file__), "webroot")
    handlers = [
        (r"/isp", ISPHandler),
        (r"/upload", UploadHandler),
        (r"/(.*)", tornado.web.StaticFileHandler, {"path": root, "default_filename": "index.html"}),
    ]
    
    app = tornado.web.Application(handlers)
    try:
        app.listen(80)
    except:
        app.listen(8080)
    
    tornado.ioloop.IOLoop.current().start()
