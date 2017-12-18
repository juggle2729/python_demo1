import random
import string

print ''.join(random.choice(string.ascii_lowercase[:6] + string.digits) for _ in range(32))
