import tornado.ioloop
import tornado.web
import os

import isp8051

ISP = None

class ISPHandler(tornado.web.RequestHandler):
    
    def get(self):
        start_address = int(self.get_argument('start', '0'))
        num_bytes = int(self.get_argument('size', '256'))
        
        #data = [45]*num_bytes        
        ISP.set_reset(True)   
        ISP.enable_programming()
        data = ISP.read_bytes(start_address,num_bytes)
        ISP.set_reset(False)         
        
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
                
        ISP.set_reset(True) 
        ISP.enable_programming()
        ISP.erase()
        ISP.write_bytes(req['start'],req['data'])
        ISP.set_reset(False) 
        
        ret = {
            'start' : req['start'],
            'size' : len(req['data'])
        }        
        
        self.set_header('Content-Type', 'application/json')
        self.write(ret)
            
if __name__ == '__main__':
    
    ISP = isp8051.ISP8051()    
    
    # WINDOWS HACK
    #import asyncio
    #asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # python-3.8.0a4
            
    root = os.path.join(os.path.dirname(__file__), "webroot")
    handlers = [
        (r"/isp", ISPHandler),
        (r"/(.*)", tornado.web.StaticFileHandler, {"path": root, "default_filename": "index.html"}),
    ]
    
    app = tornado.web.Application(handlers)
    #app.listen(8080)
    app.listen(80)    
    
    tornado.ioloop.IOLoop.current().start()
