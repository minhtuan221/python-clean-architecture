

class Middleware(object):
    def __init__(self, function): 
        self.function = function 
      
    def __call__(self, *args, **kwargs): 
  
        # We can add some code  
        # before function call 
  
        res = self.function(*args, **kwargs) 
  
        # We can also add some code 
        # after function call. 
        return res