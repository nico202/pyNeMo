python Runner.py --steps 10000 nets/lamprey_YARP_2joint_Example.vue --vue-posthook "min_angle_A=-180;max_angle_A=180;min_angle_B=min_angle_A;max_angle_B=max_angle_A;cerebellum_ctrl_a=(0,0,0);cerebellum_ctrl_b=(0,0,0)" --save-spikes --reset-and-exit --robot-mode Position
#custom-notify-send "Resetted world"
python Runner.py --steps 0 nets/lamprey_YARP_2joint_Example.vue --vue-posthook "min_angle_A=-15;max_angle_A=15;min_angle_B=min_angle_A;max_angle_B=max_angle_A" --vue-prehook "cerebellum_ctrl_a=(0,0,0);cerebellum_ctrl_b=(0,0,0)" --save-spikes --robot-mode Position --angle-images --simple-feedback --bypass-debug 50
python Runner.py --steps 10000 nets/lamprey_YARP_2joint_Example.vue --vue-posthook "min_angle_A=-180;max_angle_A=180;min_angle_B=min_angle_A;max_angle_B=max_angle_A;cerebellum_ctrl_a=(0,0,0);cerebellum_ctrl_b=(0,0,0)" --save-spikes --reset-and-exit --robot-mode Position
