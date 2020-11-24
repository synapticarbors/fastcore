# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/03_xtras.ipynb (unless otherwise specified).

__all__ = ['dict2obj', 'repr_dict', 'is_listy', 'shufflish', 'mapped', 'IterLen', 'ReindexCollection', 'open_file',
           'save_pickle', 'load_pickle', 'maybe_open', 'image_size', 'bunzip', 'join_path_file', 'urlquote', 'urlwrap',
           'urlopen', 'urlread', 'urljson', 'urlcheck', 'urlclean', 'urlsave', 'urlvalid', 'untar_dir', 'repo_details',
           'run', 'do_request', 'threaded', 'startthread', 'start_server', 'start_client', 'stringfmt_names',
           'PartialFormatter', 'partial_format', 'trace', 'round_multiple', 'modified_env', 'ContextManagers',
           'str2bool', 'sort_by_run', 'set_num_threads', 'ProcessPoolExecutor', 'ThreadPoolExecutor', 'parallel',
           'run_procs', 'parallel_gen']

# Cell
from .imports import *
from .foundation import *
from .basics import *
from functools import wraps

import mimetypes,pickle,random,json,urllib,subprocess,shlex,bz2,gzip,zipfile,tarfile
import imghdr,struct,socket,distutils.util,urllib.request,tempfile,time,string
from contextlib import contextmanager,ExitStack
from pdb import set_trace
from urllib.request import Request
from urllib.error import HTTPError,URLError
from urllib.parse import urlencode,urlparse,urlunparse
from http.client import InvalidURL
from threading import Thread

# Cell
def dict2obj(d):
    "Convert (possibly nested) dicts (or lists of dicts) to `AttrDict`"
    if isinstance(d, (L,list)): return L(d).map(dict2obj)
    if not isinstance(d, dict): return d
    return AttrDict(**{k:dict2obj(v) for k,v in d.items()})

# Cell
def _repr_dict(d, lvl):
    if isinstance(d,dict):
        its = [f"{k}: {_repr_dict(v,lvl+1)}" for k,v in d.items()]
    elif isinstance(d,(list,L)): its = [_repr_dict(o,lvl+1) for o in d]
    else: return str(d)
    return '\n' + '\n'.join([" "*(lvl*2) + "- " + o for o in its])

# Cell
def repr_dict(d):
    "Print nested dicts and lists, such as returned by `dict2obj`"
    return _repr_dict(d,0).strip()

# Cell
@patch
def __repr__(self:AttrDict): return repr_dict(self)

AttrDict._repr_markdown_ = AttrDict.__repr__

# Cell
def is_listy(x):
    "`isinstance(x, (tuple,list,L,slice,Generator))`"
    return isinstance(x, (tuple,list,L,slice,Generator))

# Cell
def shufflish(x, pct=0.04):
    "Randomly relocate items of `x` up to `pct` of `len(x)` from their starting location"
    n = len(x)
    return L(x[i] for i in sorted(range_of(x), key=lambda o: o+n*(1+random.random()*pct)))

# Cell
def mapped(f, it):
    "map `f` over `it`, unless it's not listy, in which case return `f(it)`"
    return L(it).map(f) if is_listy(it) else f(it)

# Cell
#hide
class IterLen:
    "Base class to add iteration to anything supporting `__len__` and `__getitem__`"
    def __iter__(self): return (self[i] for i in range_of(self))

# Cell
@docs
class ReindexCollection(GetAttr, IterLen):
    "Reindexes collection `coll` with indices `idxs` and optional LRU cache of size `cache`"
    _default='coll'
    def __init__(self, coll, idxs=None, cache=None, tfm=noop):
        if idxs is None: idxs = L.range(coll)
        store_attr()
        if cache is not None: self._get = functools.lru_cache(maxsize=cache)(self._get)

    def _get(self, i): return self.tfm(self.coll[i])
    def __getitem__(self, i): return self._get(self.idxs[i])
    def __len__(self): return len(self.coll)
    def reindex(self, idxs): self.idxs = idxs
    def shuffle(self): random.shuffle(self.idxs)
    def cache_clear(self): self._get.cache_clear()
    def __getstate__(self): return {'coll': self.coll, 'idxs': self.idxs, 'cache': self.cache, 'tfm': self.tfm}
    def __setstate__(self, s): self.coll,self.idxs,self.cache,self.tfm = s['coll'],s['idxs'],s['cache'],s['tfm']

    _docs = dict(reindex="Replace `self.idxs` with idxs",
                shuffle="Randomly shuffle indices",
                cache_clear="Clear LRU cache")

# Cell
@patch
def readlines(self:Path, hint=-1, encoding='utf8'):
    "Read the content of `self`"
    with self.open(encoding=encoding) as f: return f.readlines(hint)

# Cell
@patch
def mk_write(self:Path, data, encoding=None, errors=None, mode=511):
    "Make all parent dirs of `self`"
    self.parent.mkdir(exist_ok=True, parents=True, mode=mode)
    self.write_text(data, encoding=encoding, errors=errors)

# Cell
@patch
def ls(self:Path, n_max=None, file_type=None, file_exts=None):
    "Contents of path as a list"
    extns=L(file_exts)
    if file_type: extns += L(k for k,v in mimetypes.types_map.items() if v.startswith(file_type+'/'))
    has_extns = len(extns)==0
    res = (o for o in self.iterdir() if has_extns or o.suffix in extns)
    if n_max is not None: res = itertools.islice(res, n_max)
    return L(res)

# Cell
def open_file(fn, mode='r', **kwargs):
    "Open a file, with optional compression if gz or bz2 suffix"
    if isinstance(fn, io.IOBase): return fn
    fn = Path(fn)
    if   fn.suffix=='.bz2': return bz2.BZ2File(fn, mode, **kwargs)
    elif fn.suffix=='.gz' : return gzip.GzipFile(fn, mode, **kwargs)
    elif fn.suffix=='.zip': return zipfile.ZipFile(fn, mode, **kwargs)
    else: return open(fn,mode, **kwargs)

# Cell
def save_pickle(fn, o):
    "Save a pickle file, to a file name or opened file"
    with open_file(fn, 'wb') as f: pickle.dump(o, f)

# Cell
def load_pickle(fn):
    "Load a pickle file from a file name or opened file"
    with open_file(fn, 'rb') as f: return pickle.load(f)

# Cell
@patch
def __repr__(self:Path):
    b = getattr(Path, 'BASE_PATH', None)
    if b:
        try: self = self.relative_to(b)
        except: pass
    return f"Path({self.as_posix()!r})"

# Cell
@contextmanager
def maybe_open(f, mode='r', **kwargs):
    "Context manager: open `f` if it is a path (and close on exit)"
    if isinstance(f, (str,os.PathLike)):
        with open(f, mode, **kwargs) as f: yield f
    else: yield f

# Cell
def image_size(fn):
    "Tuple of (w,h) for png, gif, or jpg; `None` otherwise"
    d = dict(png=_png_size, gif=_gif_size, jpeg=_jpg_size)
    with maybe_open(fn, 'rb') as f: return d[imghdr.what(f)](f)

# Cell
def bunzip(fn):
    "bunzip `fn`, raising exception if output already exists"
    fn = Path(fn)
    assert fn.exists(), f"{fn} doesn't exist"
    out_fn = fn.with_suffix('')
    assert not out_fn.exists(), f"{out_fn} already exists"
    with bz2.BZ2File(fn, 'rb') as src, out_fn.open('wb') as dst:
        for d in iter(lambda: src.read(1024*1024), b''): dst.write(d)

# Cell
def join_path_file(file, path, ext=''):
    "Return `path/file` if file is a string or a `Path`, file otherwise"
    if not isinstance(file, (str, Path)): return file
    path.mkdir(parents=True, exist_ok=True)
    return path/f'{file}{ext}'

# Cell
_ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'

# Cell
def urlquote(url):
    "Update url's path with `urllib.parse.quote`"
    subdelims = "!$&'()*+,;="
    gendelims = ":?#[]@"
    safe = subdelims+gendelims+"%/"
    p = list(urlparse(url))
    p[2] = urllib.parse.quote(p[2], safe=safe)
    for i in range(3,6): p[i] = urllib.parse.quote(p[i], safe=safe)
    return urlunparse(p)

# Cell
def urlwrap(url, data=None, headers=None):
    "Wrap `url` in a urllib `Request` with a user-agent header"
    if not isinstance(url,Request): url = Request(urlquote(url), data=data, headers=headers or {})
    url.headers['User-Agent'] = _ua
    return url

# Cell
def urlopen(url, data=None, headers=None, **kwargs):
    "Like `urllib.request.urlopen`, but first `urlwrap` the `url`, and encode `data`"
    if kwargs and not data: data=kwargs
    if data is not None:
        if not isinstance(data, (str,bytes)): data = urlencode(data)
        if not isinstance(data, bytes): data = data.encode('ascii')
    return urllib.request.urlopen(urlwrap(url, data=data, headers=headers))

# Cell
def urlread(url, data=None, headers=None, **kwargs):
    "Retrieve `url`, using `data` dict or `kwargs` to `POST` if present"
    with urlopen(url, data=data, headers=headers, **kwargs) as res: return res.read()

# Cell
def urljson(url, data=None):
    "Retrieve `url` and decode json"
    res = urlread(url, data=data)
    return json.loads(res) if res else {}

# Cell
def urlcheck(url, timeout=10):
    if not url: return True
    try:
        with urlopen(url, timeout=timeout) as u: return u.status<400
    except URLError: return False
    except socket.timeout: return False
    except InvalidURL: return False

# Cell
def urlclean(url):
    "Remove fragment, params, and querystring from `url` if present"
    return urlunparse(urlparse(url)[:3]+('','',''))

# Cell
def urlsave(url, dest=None):
    "Retrieve `url` and save based on its name"
    res = urlread(urlwrap(url))
    if dest is None: dest = Path(url).name
    name = urlclean(dest)
    Path(name).write_bytes(res)
    return dest

# Cell
def urlvalid(x):
    "Test if `x` is a valid URL"
    return all (getattrs(urlparse(str(x)), 'scheme', 'netloc'))

# Cell
def untar_dir(file, dest):
    with tempfile.TemporaryDirectory(dir='.') as d:
        d = Path(d)
        with tarfile.open(mode='r:gz', fileobj=file) as t: t.extractall(d)
        next(d.iterdir()).rename(dest)

# Cell
def repo_details(url):
    "Tuple of `owner,name` from ssh or https git repo `url`"
    res = remove_suffix(url.strip(), '.git')
    res = res.split(':')[-1]
    return res.split('/')[-2:]

# Cell
def run(cmd, *rest, ignore_ex=False, as_bytes=False):
    "Pass `cmd` (splitting with `shlex` if string) to `subprocess.run`; return `stdout`; raise `IOError` if fails"
    if rest: cmd = (cmd,)+rest
    elif isinstance(cmd,str): cmd = shlex.split(cmd)
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = res.stdout
    if not as_bytes: stdout = stdout.decode()
    if ignore_ex: return (res.returncode, stdout)
    if res.returncode: raise IOError("{} ;; {}".format(res.stdout, res.stderr))
    return stdout

# Cell
def do_request(url, post=False, headers=None, **data):
    "Call GET or json-encoded POST on `url`, depending on `post`"
    if data:
        if post: data = json.dumps(data).encode('ascii')
        else:
            url += "?" + urlencode(data)
            data = None
    return urljson(Request(url, headers=headers, data=data or None))

# Cell
def threaded(f):
    "Run `f` in a thread, and returns the thread"
    @wraps(f)
    def _f(*args, **kwargs):
        res = Thread(target=f, args=args, kwargs=kwargs)
        res.start()
        return res
    return _f

# Cell
def startthread(f):
    "Like `threaded`, but start thread immediately"
    threaded(f)()

# Cell
def _socket_det(port,host,dgram):
    if isinstance(port,int): family,addr = socket.AF_INET,(host or socket.gethostname(),port)
    else: family,addr = socket.AF_UNIX,port
    return family,addr,(socket.SOCK_STREAM,socket.SOCK_DGRAM)[dgram]

# Cell
def start_server(port, host=None, dgram=False, reuse_addr=True, n_queue=None):
    "Create a `socket` server on `port`, with optional `host`, of type `dgram`"
    listen_args = [n_queue] if n_queue else []
    family,addr,typ = _socket_det(port,host,dgram)
    if family==socket.AF_UNIX:
        if os.path.exists(addr): os.unlink(addr)
        assert not os.path.exists(addr), f"{addr} in use"
    s = socket.socket(family, typ)
    if reuse_addr and family==socket.AF_INET: s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(*listen_args)
    return s

# Cell
def start_client(port, host=None, dgram=False):
    "Create a `socket` client on `port`, with optional `host`, of type `dgram`"
    family,addr,typ = _socket_det(port,host,dgram)
    s = socket.socket(family, typ)
    s.connect(addr)
    return s

# Cell
_fmt = string.Formatter()

# Cell
def stringfmt_names(s:str)->list:
    "Unique brace-delimited names in `s`"
    return uniqueify(o[1] for o in _fmt.parse(s) if o[1])

# Cell
class PartialFormatter(string.Formatter):
    def __init__(self):
        self.missing = set()
        super().__init__()

    def get_field(self, nm, args, kwargs):
        try: return super().get_field(nm, args, kwargs)
        except KeyError:
            self.missing.add(nm)
            return '{'+nm+'}',nm

    def check_unused_args(self, used, args, kwargs):
        self.xtra = filter_keys(kwargs, lambda o: o not in used)

# Cell
def partial_format(s:str, **kwargs):
    "string format `s`, ignoring missing field errors, returning missing and extra fields"
    fmt = PartialFormatter()
    res = fmt.format(s, **kwargs)
    return res,list(fmt.missing),fmt.xtra

# Cell
def trace(f):
    "Add `set_trace` to an existing function `f`"
    if getattr(f, '_traced', False): return f
    def _inner(*args,**kwargs):
        set_trace()
        return f(*args,**kwargs)
    _inner._traced = True
    return _inner

# Cell
def round_multiple(x, mult, round_down=False):
    "Round `x` to nearest multiple of `mult`"
    def _f(x_): return (int if round_down else round)(x_/mult)*mult
    res = L(x).map(_f)
    return res if is_listy(x) else res[0]

# Cell
@contextmanager
def modified_env(*delete, **replace):
    "Context manager temporarily modifying `os.environ` by deleting `delete` and replacing `replace`"
    prev = dict(os.environ)
    try:
        os.environ.update(replace)
        for k in delete: os.environ.pop(k, None)
        yield
    finally:
        os.environ.clear()
        os.environ.update(prev)

# Cell
class ContextManagers(GetAttr):
    "Wrapper for `contextlib.ExitStack` which enters a collection of context managers"
    def __init__(self, mgrs): self.default,self.stack = L(mgrs),ExitStack()
    def __enter__(self): self.default.map(self.stack.enter_context)
    def __exit__(self, *args, **kwargs): self.stack.__exit__(*args, **kwargs)

# Cell
def str2bool(s):
    "Case-insensitive convert string `s` too a bool (`y`,`yes`,`t`,`true`,`on`,`1`->`True`)"
    if not isinstance(s,str): return bool(s)
    return bool(distutils.util.strtobool(s)) if s else False

# Cell
def _is_instance(f, gs):
    tst = [g if type(g) in [type, 'function'] else g.__class__ for g in gs]
    for g in tst:
        if isinstance(f, g) or f==g: return True
    return False

def _is_first(f, gs):
    for o in L(getattr(f, 'run_after', None)):
        if _is_instance(o, gs): return False
    for g in gs:
        if _is_instance(f, L(getattr(g, 'run_before', None))): return False
    return True

def sort_by_run(fs):
    end = L(fs).attrgot('toward_end')
    inp,res = L(fs)[~end] + L(fs)[end], L()
    while len(inp):
        for i,o in enumerate(inp):
            if _is_first(o, inp):
                res.append(inp.pop(i))
                break
        else: raise Exception("Impossible to sort")
    return res

# Cell
from multiprocessing import Process, Queue
import concurrent.futures
from multiprocessing import Manager

# Cell
def set_num_threads(nt):
    "Get numpy (and others) to use `nt` threads"
    try: import mkl; mkl.set_num_threads(nt)
    except: pass
    try: import torch; torch.set_num_threads(nt)
    except: pass
    os.environ['IPC_ENABLE']='1'
    for o in ['OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:
        os.environ[o] = str(nt)

# Cell
def _call(lock, pause, n, g, item):
    l = False
    if pause:
        try:
            l = lock.acquire(timeout=pause*(n+2))
            time.sleep(pause)
        finally:
            if l: lock.release()
    return g(item)

# Cell
class ProcessPoolExecutor(concurrent.futures.ProcessPoolExecutor):
    "Same as Python's ProcessPoolExecutor, except can pass `max_workers==0` for serial execution"
    def __init__(self, max_workers=defaults.cpus, on_exc=print, pause=0, **kwargs):
        if max_workers is None: max_workers=defaults.cpus
        store_attr()
        self.not_parallel = max_workers==0
        if self.not_parallel: max_workers=1
        super().__init__(max_workers, **kwargs)

    def map(self, f, items, timeout=None, chunksize=1, *args, **kwargs):
        self.lock = Manager().Lock()
        g = partial(f, *args, **kwargs)
        if self.not_parallel: return map(g, items)
        _g = partial(_call, self.lock, self.pause, self.max_workers, g)
        try: return super().map(_g, items, timeout=timeout, chunksize=chunksize)
        except Exception as e: self.on_exc(e)

# Cell
class ThreadPoolExecutor(concurrent.futures.ThreadPoolExecutor):
    "Same as Python's ThreadPoolExecutor, except can pass `max_workers==0` for serial execution"
    def __init__(self, max_workers=defaults.cpus, on_exc=print, pause=0, **kwargs):
        if max_workers is None: max_workers=defaults.cpus
        store_attr()
        self.not_parallel = max_workers==0
        if self.not_parallel: max_workers=1
        super().__init__(max_workers, **kwargs)

    def map(self, f, items, timeout=None, chunksize=1, *args, **kwargs):
        self.lock = Manager().Lock()
        g = partial(f, *args, **kwargs)
        if self.not_parallel: return map(g, items)
        _g = partial(_call, self.lock, self.pause, self.max_workers, g)
        try: return super().map(_g, items, timeout=timeout, chunksize=chunksize)
        except Exception as e: self.on_exc(e)

# Cell
try: from fastprogress import progress_bar
except: progress_bar = None

# Cell
def parallel(f, items, *args, n_workers=defaults.cpus, total=None, progress=None, pause=0,
             threadpool=False, timeout=None, chunksize=1, **kwargs):
    "Applies `func` in parallel to `items`, using `n_workers`"
    if progress is None: progress = progress_bar is not None
    pool = ThreadPoolExecutor if threadpool else ProcessPoolExecutor
    with pool(n_workers, pause=pause) as ex:
        r = ex.map(f,items, *args, timeout=timeout, chunksize=chunksize, **kwargs)
        if progress:
            if total is None: total = len(items)
            r = progress_bar(r, total=total, leave=False)
        return L(r)

# Cell
def run_procs(f, f_done, args):
    "Call `f` for each item in `args` in parallel, yielding `f_done`"
    processes = L(args).map(Process, args=arg0, target=f)
    for o in processes: o.start()
    yield from f_done()
    processes.map(Self.join())

# Cell
def _f_pg(obj, queue, batch, start_idx):
    for i,b in enumerate(obj(batch)): queue.put((start_idx+i,b))

def _done_pg(queue, items): return (queue.get() for _ in items)

# Cell
def parallel_gen(cls, items, n_workers=defaults.cpus, **kwargs):
    "Instantiate `cls` in `n_workers` procs & call each on a subset of `items` in parallel."
    if n_workers==0:
        yield from enumerate(list(cls(**kwargs)(items)))
        return
    batches = L(chunked(items, n_chunks=n_workers))
    idx = L(itertools.accumulate(0 + batches.map(len)))
    queue = Queue()
    if progress_bar: items = progress_bar(items, leave=False)
    f=partial(_f_pg, cls(**kwargs), queue)
    done=partial(_done_pg, queue, items)
    yield from run_procs(f, done, L(batches,idx).zip())