// Professional Vertebrae 3D Viewer
// High-quality rendering matching PyVista visualization

let scene, camera, renderer;
let vertebraeMeshes = {};
let currentPatient = null;
let currentProcessingType = 'raw'; // 'raw' or 'cleaned'
let patientData = {};

// Vertebrae groups
const VERTEBRAE_GROUPS = {
    cervical: ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7'],
    thoracic: ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12'],
    lumbar: ['L1', 'L2', 'L3', 'L4', 'L5']
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);

function init() {
    setupScene();
    setupLighting();
    setupControls();
    populateVertebraeList();
    setupEventListeners();
    animate();
    console.log('✓ Viewer initialized');
}

function setupScene() {
    const canvas = document.getElementById('canvas');
    const container = document.querySelector('.viewer-container');
    
    // Create scene with dark background
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0f0f1e);
    
    // Setup camera
    camera = new THREE.PerspectiveCamera(
        45,
        container.clientWidth / container.clientHeight,
        0.1,
        10000
    );
    camera.position.set(400, 400, 400);
    camera.lookAt(0, 0, 0);
    
    // Setup renderer with high quality settings
    renderer = new THREE.WebGLRenderer({ 
        canvas: canvas, 
        antialias: true,
        alpha: true
    });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    
    // Handle window resize
    window.addEventListener('resize', onWindowResize);
}

function setupLighting() {
    // Ambient light for base illumination
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    
    // Main directional light (matching PyVista position (1,1,1))
    const mainLight = new THREE.DirectionalLight(0xffffff, 0.8);
    mainLight.position.set(1, 1, 1).normalize().multiplyScalar(500);
    mainLight.castShadow = true;
    scene.add(mainLight);
    
    // Fill light from opposite side
    const fillLight = new THREE.DirectionalLight(0xffffff, 0.3);
    fillLight.position.set(-1, -1, -1).normalize().multiplyScalar(500);
    scene.add(fillLight);
    
    // Top light for better visibility
    const topLight = new THREE.DirectionalLight(0xffffff, 0.4);
    topLight.position.set(0, 1, 0).multiplyScalar(500);
    scene.add(topLight);
    
    // Add center point marker (small sphere to show center)
    const centerGeometry = new THREE.SphereGeometry(2, 16, 16);
    const centerMaterial = new THREE.MeshBasicMaterial({ 
        color: 0xff0000,
        opacity: 0.5,
        transparent: true
    });
    const centerMarker = new THREE.Mesh(centerGeometry, centerMaterial);
    scene.add(centerMarker);
}

function setupControls() {
    let isMouseDown = false;
    let isPanning = false;
    let mouseX = 0, mouseY = 0;
    let targetRotationX = 0, targetRotationY = 0;
    
    const canvas = document.getElementById('canvas');
    
    canvas.addEventListener('mousedown', (e) => {
        isMouseDown = true;
        isPanning = (e.button === 2);
        mouseX = e.clientX;
        mouseY = e.clientY;
        e.preventDefault();
    });
    
    canvas.addEventListener('mousemove', (e) => {
        if (!isMouseDown) return;
        
        const deltaX = e.clientX - mouseX;
        const deltaY = e.clientY - mouseY;
        
        if (isPanning) {
            camera.position.x += deltaX * 0.5;
            camera.position.y -= deltaY * 0.5;
        } else {
            targetRotationY += deltaX * 0.01;
            targetRotationX += deltaY * 0.01;
            
            const radius = Math.sqrt(
                camera.position.x ** 2 + 
                camera.position.y ** 2 + 
                camera.position.z ** 2
            );
            
            camera.position.x = radius * Math.sin(targetRotationY) * Math.cos(targetRotationX);
            camera.position.y = radius * Math.sin(targetRotationX);
            camera.position.z = radius * Math.cos(targetRotationY) * Math.cos(targetRotationX);
            
            camera.lookAt(0, 0, 0);
        }
        
        mouseX = e.clientX;
        mouseY = e.clientY;
    });
    
    canvas.addEventListener('mouseup', () => {
        isMouseDown = false;
        isPanning = false;
    });
    
    canvas.addEventListener('contextmenu', (e) => e.preventDefault());
    
    canvas.addEventListener('wheel', (e) => {
        e.preventDefault();
        const delta = e.deltaY * 0.1;
        const direction = camera.position.clone().normalize();
        camera.position.add(direction.multiplyScalar(delta));
    });
}

function setupEventListeners() {
    document.getElementById('patient-select').addEventListener('change', function() {
        if (this.value) {
            currentPatient = this.value;
            loadPatient(currentPatient, currentProcessingType);
        }
    });
    
    document.getElementById('processing-select').addEventListener('change', function() {
        currentProcessingType = this.value;
        if (currentPatient) {
            loadPatient(currentPatient, currentProcessingType);
        }
    });
}

function populateVertebraeList() {
    Object.entries(VERTEBRAE_GROUPS).forEach(([group, vertebrae]) => {
        const container = document.getElementById(`${group}-group`);
        
        vertebrae.forEach(name => {
            const item = document.createElement('div');
            item.className = 'vertebra-item';
            item.dataset.name = name;
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'vertebra-checkbox';
            checkbox.id = `check-${name}`;
            checkbox.checked = true;
            checkbox.addEventListener('change', () => toggleVertebra(name, checkbox.checked));
            
            const colorBox = document.createElement('div');
            colorBox.className = 'vertebra-color';
            colorBox.id = `color-${name}`;
            
            const label = document.createElement('span');
            label.className = 'vertebra-name';
            label.textContent = name;
            
            item.appendChild(checkbox);
            item.appendChild(colorBox);
            item.appendChild(label);
            
            item.addEventListener('click', (e) => {
                if (e.target !== checkbox) {
                    checkbox.checked = !checkbox.checked;
                    checkbox.dispatchEvent(new Event('change'));
                }
            });
            
            container.appendChild(item);
        });
    });
}

async function loadPatient(patientId, processingType = 'raw') {
    currentPatient = patientId;
    currentProcessingType = processingType;
    showLoading(true);
    
    // Determine folder based on processing type
    const folder = processingType === 'cleaned' ? `${patientId}_cleaned` : patientId;
    const processingLabel = processingType === 'cleaned' ? 'Post-Processed' : 'Raw Prediction';
    
    console.log(`Loading patient: ${patientId} (${processingLabel})`);
    
    try {
        // Load patient metadata
        const response = await fetch(`web_data/${folder}/metadata.json`);
        if (!response.ok) throw new Error(`Failed to load ${processingLabel} data for patient ${patientId}`);
        
        const data = await response.json();
        patientData = data;
        
        // Clear existing meshes
        clearMeshes();
        
        // Load all vertebrae
        const vertebrae = data.vertebrae;
        let loadedCount = 0;
        const totalCount = Object.keys(vertebrae).length;
        
        document.querySelector('.loading-text').textContent = `Loading ${processingLabel}...`;
        
        for (const [name, info] of Object.entries(vertebrae)) {
            await loadVertebra(name, info);
            loadedCount++;
            console.log(`Loaded ${loadedCount}/${totalCount}: ${name}`);
        }
        
        // Update color boxes in UI
        updateColorBoxes();
        
        // Center the loaded data
        centerScene();
        
        // Reset camera
        resetCamera();
        
        // Update status badge
        updateStatusBadge(processingType);
        
        showLoading(false);
        console.log(`✓ Patient loaded successfully (${processingLabel})`);
        
    } catch (error) {
        console.error('Error loading patient:', error);
        showLoading(false);
        alert(`Failed to load patient: ${error.message}`);
    }
}

function centerScene() {
    // Calculate bounding box of all meshes
    const box = new THREE.Box3();
    
    Object.values(vertebraeMeshes).forEach(mesh => {
        box.expandByObject(mesh);
    });
    
    // Get center of bounding box
    const center = new THREE.Vector3();
    box.getCenter(center);
    
    // Move all meshes so center is at origin
    Object.values(vertebraeMeshes).forEach(mesh => {
        mesh.position.sub(center);
    });
    
    console.log('Scene centered at origin');
}

async function loadVertebra(name, info) {
    try {
        const response = await fetch(info.file);
        if (!response.ok) throw new Error(`Failed to load ${name}`);
        
        const meshData = await response.json();
        
        // Create Three.js geometry
        const geometry = new THREE.BufferGeometry();
        
        // Add vertices
        const vertices = new Float32Array(meshData.vertices.flat());
        geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
        
        // Add faces (indices)
        const indices = new Uint32Array(meshData.faces.flat());
        geometry.setIndex(new THREE.BufferAttribute(indices, 1));
        
        // Compute normals for smooth shading
        geometry.computeVertexNormals();
        
        // Create material with PyVista-like appearance
        const color = new THREE.Color(info.color);
        const material = new THREE.MeshPhongMaterial({
            color: color,
            shininess: 30,        // Matching PyVista specular_power
            specular: 0xffffff,   // Matching PyVista specular=1.0
            flatShading: false,   // Smooth shading like PyVista
            side: THREE.DoubleSide
        });
        
        // Create mesh
        const mesh = new THREE.Mesh(geometry, material);
        mesh.name = name;
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        
        // Store and add to scene
        vertebraeMeshes[name] = mesh;
        scene.add(mesh);
        
    } catch (error) {
        console.error(`Error loading ${name}:`, error);
    }
}

function clearMeshes() {
    Object.values(vertebraeMeshes).forEach(mesh => {
        scene.remove(mesh);
        mesh.geometry.dispose();
        mesh.material.dispose();
    });
    vertebraeMeshes = {};
}

function toggleVertebra(name, visible) {
    const mesh = vertebraeMeshes[name];
    if (mesh) {
        mesh.visible = visible;
    }
}

function updateColorBoxes() {
    if (!patientData.vertebrae) return;
    
    Object.entries(patientData.vertebrae).forEach(([name, info]) => {
        const colorBox = document.getElementById(`color-${name}`);
        if (colorBox) {
            colorBox.style.backgroundColor = info.color;
        }
    });
}

function setView(mode) {
    document.querySelectorAll('.view-btn-nav').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    const distance = 450;
    
    switch(mode) {
        case '3d':
            camera.position.set(distance, distance, distance);
            break;
        case 'front':
            camera.position.set(0, 0, distance);
            break;
        case 'side':
            camera.position.set(distance, 0, 0);
            break;
        case 'top':
            camera.position.set(0, distance, 0);
            break;
    }
    
    camera.lookAt(0, 0, 0);
}

function toggleDropdown() {
    const dropdown = document.getElementById('vertebrae-dropdown');
    const arrow = document.getElementById('dropdown-arrow');
    
    if (dropdown.classList.contains('show')) {
        dropdown.classList.remove('show');
        arrow.textContent = '▼';
    } else {
        dropdown.classList.add('show');
        arrow.textContent = '▲';
    }
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const dropdown = document.getElementById('vertebrae-dropdown');
    const toggleBtn = event.target.closest('.toggle-btn');
    
    if (!toggleBtn && !dropdown.contains(event.target)) {
        dropdown.classList.remove('show');
        document.getElementById('dropdown-arrow').textContent = '▼';
    }
});

function resetCamera() {
    camera.position.set(400, 400, 400);
    camera.lookAt(0, 0, 0);
}

function toggleGroup(groupName) {
    const group = document.getElementById(`${groupName}-group`);
    const toggle = document.getElementById(`${groupName}-toggle`);
    
    if (group.style.display === 'none') {
        group.style.display = 'block';
        toggle.textContent = '▼';
        toggle.style.transform = 'rotate(0deg)';
    } else {
        group.style.display = 'none';
        toggle.textContent = '▶';
        toggle.style.transform = 'rotate(-90deg)';
    }
}

function selectAll() {
    Object.keys(vertebraeMeshes).forEach(name => {
        const checkbox = document.getElementById(`check-${name}`);
        if (checkbox) {
            checkbox.checked = true;
            toggleVertebra(name, true);
        }
    });
}

function deselectAll() {
    Object.keys(vertebraeMeshes).forEach(name => {
        const checkbox = document.getElementById(`check-${name}`);
        if (checkbox) {
            checkbox.checked = false;
            toggleVertebra(name, false);
        }
    });
}

function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'block' : 'none';
}

function updateStatusBadge(processingType) {
    const badge = document.getElementById('status-badge');
    const badgeValue = badge.querySelector('.badge-value');
    
    if (processingType === 'cleaned') {
        badge.classList.add('cleaned');
        badgeValue.textContent = 'Post-Processed';
    } else {
        badge.classList.remove('cleaned');
        badgeValue.textContent = 'Raw Prediction';
    }
    
    badge.style.display = 'block';
}

function onWindowResize() {
    const container = document.querySelector('.viewer-container');
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
}

function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}

console.log('✓ App loaded');
