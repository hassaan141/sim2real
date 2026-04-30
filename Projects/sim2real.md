Start by making the **real setup intentionally simple**. Your instinct is right: small brown desk, white wall, fixed camera, fixed cup, fixed robot base. That is exactly how you make sim2real easier.

The key idea is this:

```text
Do not try to perfectly simulate everything.
Make the real world easier, then randomize the sim around that simpler world.
```

For your marker-sorting task, model these parts first:

1. **Robot**
   Use the SO100 URDF/MJCF -> USD pipeline so joint limits, link geometry, and gripper motion are roughly correct.

2. **Table and wall**
   These matter mostly for:
   - collisions
   - camera background
   - lighting consistency
   - stable reference frame

   Keep them fixed in both sim and real.

3. **Cup/container**
   Model its:
   - size
   - pose
   - opening diameter
   - height

   This matters more than tiny material details.

4. **Marker**
   Yes, weight matters, but not first.
   First get:
   - shape
   - size
   - contact geometry
   - center of mass approximation
   - friction
   - graspability

   Then tune:
   - mass
   - friction
   - restitution

For learning, the best order is:

```text
1. Reach marker
2. Grasp marker
3. Lift marker
4. Move to cup
5. Drop into cup
6. Full sorting task
```

Do not start with the full task.

For sim2real, focus on matching the things that affect success most:

- robot kinematics
- gripper closing behavior
- marker size/shape
- table height
- cup pose
- camera pose
- lighting range
- friction/contact behavior

You do **not** need perfect physics. You need the policy to be robust.

Lightwheel can help here if we use it carefully. Their SimReady assets are useful because they are meant to include more than visual meshes: geometry, physical properties, collision/contact behavior, and robotics-friendly USD/MJCF packaging. That is exactly the category of data that is painful to hand-tune for sim2real.

Use Lightwheel assets for:

- table/desk assets, if the dimensions are close to the real desk
- cup/container assets, especially if collision geometry and opening size are authored well
- marker-like rigid objects, if there is a close cylindrical pen/marker asset
- clutter or background props later, after the core task works

Do not use a nice-looking asset just because it is available. For this task, a visually realistic cup with the wrong opening, mass, or collision mesh is worse than a boring primitive cup with the right dimensions.

The right asset workflow is:

```text
1. Measure the real object.
2. Pick the closest SimReady asset.
3. Check scale, origin, collision geometry, mass, inertia, and friction.
4. Spawn it in Isaac Lab as a USD asset.
5. Run simple contact tests before training.
6. Randomize around the measured values.
```

The primitive scene should stay as the baseline. Then Lightwheel assets become upgrades, not dependencies. In the current script, the intended pattern is:

```bash
python 02_Sim2Real/marker_pick_place.py \
  --table-usd /path/to/lightwheel/table.usd \
  --cup-usd /path/to/lightwheel/cup.usd \
  --marker-usd /path/to/lightwheel/marker.usd
```

If only one good asset is available, use only that one. For example, replacing the cup first is probably more valuable than replacing the table, because the cup opening and collision geometry directly affect success.

So the practical recipe is:

```text
fixed real scene
+ approximate sim scene
+ domain randomization
+ staged task training
```

Randomize in sim:

- marker spawn pose
- marker mass a little
- friction a little
- lighting
- camera noise
- cup pose slightly
- table texture/color slightly

But keep the world structure fixed.

If you want to do this well, the next thing to design is not the whole physics model. It is the **task specification**:

```text
observations
actions
reward
reset conditions
success condition
```

That is the real backbone. After that, we define exactly what needs to be modeled in the scene.
