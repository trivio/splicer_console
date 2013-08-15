import os
from itertools import islice, tee

from splicer.ast import JoinOp, LoadOp
from texttable import Texttable


def init(dataset):
  dataset.set_dump_func(dump)

def take(n, iterable):
  "Return first n items of the iterable as a list"
  return list(islice(iterable, n))

def explain(query_or_op, indent = 0):
  if hasattr(query_or_op, 'operations'):
    explain(query_or_op.operations)
    return
  

  op = query_or_op

  p = []

  if indent:
    p.append('+')
    
  p.append(("-" * indent) + op.__class__.__name__)
  p.append("(")

  params = []
  for name in op.__slots__:
    if name not in ('left', 'right', 'relation'):
      params.append("{}={}".format(name, getattr(op, name)))
  p.append(",".join(params))

  p.append(")")

  print "".join(p)

  if isinstance(op,JoinOp):
    explain(op.left, indent+1)
    explain(op.right, indent+1)
  elif not isinstance(op, LoadOp):
    explain(op.relation, indent+1)

  


def dump(relation):
  width,height = term_size()
  table = Texttable(width)


  sample, iterator = tee(relation)


  table.add_rows(take(1000,sample))
  table._compute_cols_width()
  del sample
  
  table.reset()

  table.set_deco(Texttable.HEADER)
  table.header([f.name for f in relation.schema.fields])



  rows = take(height-3, iterator)

  try:
    while rows:
      table.add_rows(rows, header=False)
      print table.draw()
      rows = take(height-3, iterator)
      if rows:
        raw_input("-- enter for more ^c to quit --")
  except KeyboardInterrupt:
    print


def term_size():
  import os
  env = os.environ
  def ioctl_GWINSZ(fd):
    try:
        import fcntl, termios, struct, os
        cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
    '1234'))
    except:
        return
    return cr
  cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
  if not cr:
    try:
      fd = os.open(os.ctermid(), os.O_RDONLY)
      cr = ioctl_GWINSZ(fd)
      os.close(fd)
    except:
      pass
  if not cr:
    cr = (env.get('LINES', 25), env.get('COLUMNS', 80))

  return int(cr[1]), int(cr[0])
