import time
from car.cart.set_power import start_machine
from car.task_func import task_baseline
from car.component import motor_UD, motor_LR, limit_switch
start_machine()


# ### 换物底层(基线+up 1s)
# task_baseline()
# motor_UD.motor_rotate(100)
# time.sleep(1)
# motor_UD.motor_rotate(0)
# time.sleep(5)

### 换物高层(基线+up 8s)
task_baseline()
# motor_UD.motor_rotate(100)
# time.sleep(8)
# motor_UD.motor_rotate(0)
# time.sleep(5)

