import os
import random
import string

n = 20

random_string = "".join(random.choices(string.ascii_letters+string.digits,k=n))
# os.environ['secret_key'] = str(random_string)
print(os.environ['secret_key'])