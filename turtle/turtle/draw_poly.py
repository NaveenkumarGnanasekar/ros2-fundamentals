import rclpy 
import math
from rclpy.node import Node 
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist

class draw_poly(Node):
    def __init__(self):
        super().__init__("draw_poly")

        self.pub = self.create_publisher(Twist,"/turtle1/cmd_vel",10)
        self.sub = self.create_subscription(Pose,"/turtle1/pose",self.pose_callback,10)
        self.timer = self.create_timer(0.05,self.drawpoly)
        self.sub
        self.current_pose = None 
        self.start_pose = None 
        self.flag = "wait"

        self.declare_parameter('sides',3)
        self.declare_parameter('length',2.0)



        self.sides = self.get_parameter('sides').value
        self.length = self.get_parameter('length').value

        self.length_tor = 0.01
        self.angular_tor = 0.01


        self.k_linear = 1.0
        self.k_angular =2.0

        self.side_com = 0 

        self.max_linear = 2.0
        self.max_angular = 2.0

    def pose_callback(self,pose:Pose):
        self.current_pose = pose

    def drawpoly(self):
        if not self.current_pose:
            return 

        twist = Twist()

        if self.flag == "wait":
            self.start_pose = self.current_pose
            self.flag = "forward"

        elif self.flag == "forward":
            dist = math.sqrt((self.current_pose.x - self.start_pose.x)**2 + (self.current_pose.y - self.start_pose.y)**2)

            error = self.length - dist

            if error <= self.length_tor:
                twist.linear.x = 0.0
                self.flag = "turn"
                self.pub.publish(twist)
                self.start_pose=self.current_pose

            else:
                speed = self.k_linear * error
                twist.linear.x = min(speed,self.max_linear)

        elif self.flag == "turn":

            angle = (2*math.pi)/self.sides

            turned_angle = self.normalize(self.current_pose.theta - self.start_pose.theta)

            error = angle - turned_angle

            if error <= self.angular_tor:
                twist.angular.z = 0.0
                self.pub.publish(twist)
                self.side_com+=1

                if self.side_com == self.sides:
                    rclpy.shutdown()
                    return 
                else:
                    self.start_pose = self.current_pose

                    self.flag = "forward"
            else:
                speed = error * self.k_angular
                twist.angular.z = min(speed , self.max_angular)

        self.pub.publish(twist)
    def normalize(self,angle):
        if angle < 0 :
            angle += 2*math.pi
        return angle 

    
def main():
    rclpy.init()
    node=draw_poly()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
