// Set up scene, camera, renderer
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
camera.position.z = 300;

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Add OrbitControls
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.enableZoom = true;

// Base
const base = new THREE.Mesh(
  new THREE.CylinderGeometry(10, 10, 20, 32),
  new THREE.MeshStandardMaterial({ color: 0x444444 })
);
scene.add(base);

// Arm segments
const arm1Length = 100;
const arm2Length = 100;

const joint1 = new THREE.Mesh(
  new THREE.BoxGeometry(arm1Length, 10, 10),
  new THREE.MeshStandardMaterial({ color: 0xff0000 })
);
joint1.position.set(arm1Length / 2, 0, 0);
scene.add(joint1);

const joint2 = new THREE.Mesh(
  new THREE.BoxGeometry(arm2Length, 10, 10),
  new THREE.MeshStandardMaterial({ color: 0x0000ff })
);
joint2.position.set(joint1.position.x + arm2Length / 2, 0, 0);
scene.add(joint2);

// Yellow joint sphere
const jointSphere = new THREE.Mesh(
  new THREE.SphereGeometry(5, 32, 32),
  new THREE.MeshBasicMaterial({ color: 0xffff00 })
);
scene.add(jointSphere);

// Lighting
scene.add(new THREE.AmbientLight(0x888888));
const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(100, 100, 100).normalize();
scene.add(directionalLight);

// Update arm function
function updateArm(theta1, theta2) {
    const t1 = THREE.Math.degToRad(theta1);
    const t2 = THREE.Math.degToRad(theta2);

    const jointX = arm1Length * Math.cos(t1);
    const jointY = arm1Length * Math.sin(t1);

    joint1.rotation.z = t1;
    joint2.position.set(jointX, jointY, 0);
    joint2.rotation.z = t1 + t2;

    jointSphere.position.set(jointX, jointY, 0);
}

// Form handler
document.getElementById("moveBtn").addEventListener("click", async () => {
    const x = parseFloat(document.getElementById("xCoord").value);
    const y = parseFloat(document.getElementById("yCoord").value);

    const res = await fetch("/api/ik", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ x, y })
    });
    const data = await res.json();
    if (data.success) {
        updateArm(data.theta1, data.theta2);
    } else {
        alert("Target is unreachable.");
    }
});

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}
animate();
