import os, queue, tempfile
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


READYDIR = os.getenv('READYDIR','/tmp')


class PidFileWatcher(FileSystemEventHandler):

    def __init__(self, *filenames,
                 filedir=READYDIR, debug=False):
        super()
        self.debug = debug
        self.q = queue.Queue()
        self.ob = Observer()
        if not filedir.endswith('/'):
            filedir += '/'
            pass
        self.to_match = set(filedir + f
                            for f in filenames)
        self.ob.schedule(self, path=filedir)
        self.ob.start()
    
    def dprint(self, *a, **kw):
        if self.debug:
            print(*a, **kw)
                
    def activated(self, evt):
        if evt.src_path in self.to_match:
            self.q.put((evt.event_type, evt.src_path))

    def on_modified(self, event):
        return self.activated(event)

    def on_created(self, event):
        return self.activated(event)

    def read_pid_file(self, path):
        try:
            with open(path) as f:
                return int(f.read())
        except FileNotFoundError:
            self.dprint("PID File Does Not Exist, Failure!")
            return 0

    def verify_pid(self, pid):
        try:
            os.kill(pid, 0) # test process existence
            self.dprint("Process Exists!  Success!")
            return True
        except ProcessLookupError:
            self.dprint("Process Lookup Error, Failure!")
            return False
        except PermissionError:
            self.dprint("Process Exists!  Success! (we don't own it)")
            return True

    def verify_pid_file(self, path):
        self.dprint("verifying", path)
        if pid := self.read_pid_file(path):
            return self.verify_pid(pid)
        return False
            
    def verify_all(self):
        self.dprint("verify all", self.to_match)
        for fn in list(self.to_match):
            if self.verify_pid_file(fn):
                self.to_match.remove(fn)

    def wait(self):
        self.dprint("INIT", self.to_match)
        self.verify_all()
        self.dprint("PRE-", self.to_match)
        while self.to_match:
            operation, fn = self.q.get()
            if self.verify_pid_file(fn):
                self.to_match.remove(fn)
                pass
            self.dprint("POST", self.to_match)
            pass
        self.ob.stop()
        self.ob.join()


def basename(path):
    return path.split('/')[-1].split('.')[0]


def write_pid_file(filename, filedir=READYDIR):
    tmp = tempfile.NamedTemporaryFile(mode='w', delete=False)
    with tmp as f:
        f.write(str(os.getpid()))
        pass
    os.replace(tmp.name, filedir + '/' + filename)
    return prog
