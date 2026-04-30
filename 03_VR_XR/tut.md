# Quest 2 Teleop for Isaac Sim / Isaac Lab

## 1. What you are trying to build

A VR teleop loop:

```text
Quest 2 headset/controllers or hand tracking
        ↓
CloudXR / OpenXR / WebXR
        ↓
Isaac Sim XR runtime
        ↓
Isaac Lab teleop device
        ↓
Retargeter maps hand/controller motion to EE pose + gripper
        ↓
Robot arm moves in sim
        ↓
Optionally record demos for imitation learning
```

Do **not** start from random script-editor snippets like the screenshot. Start from NVIDIA’s official teleop stack, then only drop lower-level if needed.

---

## 2. Main docs and libraries to read

| Priority | Resource                                  | Use it for                                                                                                                                                                                                                                               |
| -------- | ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1        | **Isaac Teleop Quick Start**              | Best starting point for Quest-style XR teleop. It installs `isaacteleop`, starts CloudXR, opens firewall ports, and connects an XR headset through a browser client. It explicitly covers Meta Quest / Pico WebXR flow. ([NVIDIA GitHub][1])             |
| 2        | **Isaac Lab CloudXR Teleoperation Guide** | Official Isaac Lab guide for XR teleop. It explains CloudXR, Isaac Lab, OpenXR, AR panel, headset connection, and robot control. It says Quest 3 and Pico 4 Ultra support are early access in the Isaac Lab CloudXR workflow. ([isaac-sim.github.io][2]) |
| 3        | **Isaac Lab Teleoperation + Mimic**       | For recording demonstrations and imitation learning. It gives the exact scripts for keyboard, SpaceMouse, and `handtracking`, plus HDF5 demo recording/replay. ([isaac-sim.github.io][3])                                                                |
| 4        | **Isaac Lab devices API**                 | Read this when you want to understand the code path. `OpenXRDevice` receives hand/head tracking data and can return raw tracking data or retargeted robot commands. ([isaac-sim.github.io][4])                                                           |
| 5        | **Retargeters in Isaac Lab**              | This is the key concept. `Se3AbsRetargeter` maps hand position to end-effector position, `Se3RelRetargeter` maps relative motion, and `GripperRetargeter` maps thumb-index distance to gripper command. ([isaac-sim.github.io][2])                       |
| 6        | **Isaac Sim OpenXR extension**            | Low-level Isaac Sim XR support. Use this if you need to enable OpenXR directly with `--enable isaacsim.xr.openxr` or through the Extension Manager. ([docs.isaacsim.omniverse.nvidia.com][5])                                                            |
| 7        | **NVIDIA CloudXR.js samples**             | Useful specifically because you have a Quest 2. The CloudXR.js samples list Quest 2/3/3S and Pico 4 Ultra as browser XR clients. ([GitHub][6])                                                                                                           |
| 8        | **NVlabs COLLAB-SIM**                     | Closest to the YouTube-style VR robot-arm teleop setup. It is a research package for Isaac Sim + XR + cuRobo MPC teleoperation and demo collection. ([GitHub][7])                                                                                        |

---

## 3. Quest 2 reality check

For your **Quest 2**, the most realistic path is:

```text
IsaacTeleop / CloudXR.js WebXR client
```

The newer Isaac Teleop docs mention Quest/Pico browser-based connection, and the CloudXR.js samples explicitly list **Quest 2/3/3S** as supported XR browser clients. ([NVIDIA GitHub][1])

The Isaac Lab CloudXR page currently calls out **Meta Quest 3** and Pico 4 Ultra as early-access devices, so Quest 2 may work through the CloudXR.js/WebXR route, but expect some version/debug friction. ([isaac-sim.github.io][2])

---

## 4. First setup path I would try

### A. Install Isaac Teleop

```bash
git clone https://github.com/NVIDIA/IsaacTeleop.git
cd IsaacTeleop

pip install 'isaacteleop[cloudxr,retargeters]~=1.0.0' \
  --extra-index-url https://pypi.nvidia.com
```

The Isaac Teleop quick start gives this exact install flow. ([NVIDIA GitHub][1])

### B. Start CloudXR

```bash
python -m isaacteleop.cloudxr --accept-eula
```

Keep this terminal running.

### C. Open ports

```bash
sudo ufw allow 47998/udp
sudo ufw allow 49100,48322/tcp
sudo ufw allow 8080,8443/tcp
```

These are the Quest/Pico WebXR client ports from the Isaac Teleop guide. ([NVIDIA GitHub][1])

### D. Connect Quest 2

Open the Isaac Teleop web client from the Quest browser and enter your workstation IP. The docs say the prebuilt client is hosted by NVIDIA, so you do not need to build a Quest app for first validation. ([NVIDIA GitHub][1])

### E. Source CloudXR env

```bash
source ~/.cloudxr/run/cloudxr.env
```

The CloudXR env points OpenXR to the CloudXR runtime. ([NVIDIA GitHub][1])

### F. Run Isaac Lab teleop test

Start with Franka stack because it is the cleanest arm teleop example:

```bash
./isaaclab.sh -p scripts/environments/teleoperation/teleop_se3_agent.py \
  --task Isaac-Stack-Cube-Franka-IK-Abs-v0 \
  --teleop_device handtracking \
  --device cpu
```

The Isaac Lab docs recommend the absolute IK task variant with `--teleop_device handtracking` for XR hand-tracking teleop. ([isaac-sim.github.io][3])

---

## 5. If you want the YouTube-style research setup

Use **COLLAB-SIM** after the official path works.

COLLAB-SIM is built for VR teleoperation in Isaac Sim, using Isaac Sim XR, controller/HMD 6-DoF state streaming, cuRobo, and MPC-style control. ([GitHub][7])

For Quest, its install docs use:

```text
Quest → ALVR → SteamVR → Isaac Sim VR/SteamVR extension
```

It says the system was tested with Quest, HTC, and Valve Index, and for Quest it uses ALVR plus SteamVR before connecting to Isaac Sim. ([GitHub][8])

I would treat COLLAB-SIM as a second-stage project because it is more research-code and version-specific.

---

## 6. What to read first, in exact order

1. **Isaac Teleop Quick Start**
2. **Isaac Lab CloudXR Teleoperation**
3. **Isaac Lab Teleoperation and Imitation Learning with Mimic**
4. **Isaac Lab devices API: `OpenXRDevice`, `DeviceBase`, retargeters**
5. **CloudXR.js samples**
6. **COLLAB-SIM install + run docs**

That order gets you from “Quest connected” to “robot arm moving” to “demo recording” without going too deep into XR internals first.

---

## 7. Interview explanation

“I set up a VR teleoperation pipeline where XR headset inputs are streamed through CloudXR/OpenXR into Isaac Lab. Isaac Lab’s teleop device receives hand or controller tracking data, then retargeters convert that data into robot actions such as end-effector pose commands and gripper commands. Once the robot can be controlled in simulation, I can record demonstrations into datasets and use them for imitation learning or Isaac Lab Mimic-style data generation.”

[1]: https://nvidia.github.io/IsaacTeleop/main/getting_started/quick_start.html "Quick Start — Isaac Teleop Documentation"
[2]: https://isaac-sim.github.io/IsaacLab/main/source/how-to/cloudxr_teleoperation.html "Setting up CloudXR Teleoperation — Isaac Lab Documentation"
[3]: https://isaac-sim.github.io/IsaacLab/main/source/overview/imitation-learning/teleop_imitation.html "Teleoperation and Imitation Learning with Isaac Lab Mimic — Isaac Lab Documentation"
[4]: https://isaac-sim.github.io/IsaacLab/main/source/api/lab/isaaclab.devices.html "isaaclab.devices — Isaac Lab Documentation"
[5]: https://docs.isaacsim.omniverse.nvidia.com/4.5.0/py/source/extensions/isaacsim.xr.openxr/docs/index.html "[isaacsim.xr.openxr] Isaac Sim OpenXR support — Isaac Sim"
[6]: https://github.com/NVIDIA/cloudxr-js-samples "GitHub - NVIDIA/cloudxr-js-samples: The samples for CloudXR.js, a JavaScript Client SDK that enables developers to build enterprise web applications for streaming high-performance VR and AR content from the CloudXR Runtime. · GitHub"
[7]: https://github.com/NVlabs/collab-sim "GitHub - NVlabs/collab-sim: Research package for MPC VR teleop with Isaac Sim and cuRobo · GitHub"
[8]: https://github.com/NVlabs/collab-sim/blob/release/docs/install_docs.md "collab-sim/docs/install_docs.md at release · NVlabs/collab-sim · GitHub"
