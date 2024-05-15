let watchId;
let startPosition;
let totalDistance = 0;
let isTracking = false;

function toggleTracking() {
    if (!isTracking) {
        startTracking();
        document.getElementById('toggleButton').innerText = "Pause Tracking";
    } else {
        stopTracking();
        document.getElementById('toggleButton').innerText = "Resume Tracking";
    }
    isTracking = !isTracking;
}

function startTracking() {
    if ('geolocation' in navigator) {
        watchId = navigator.geolocation.watchPosition(updatePosition, positionError);
        startPosition = null;
        totalDistance = 0;
    } else {
        alert('Geolocation is not available in your browser.');
    }
}

function stopTracking() {
    if (watchId) {
        navigator.geolocation.clearWatch(watchId);
        watchId = null;
    }
    totalDistance = 0;
    updateDistanceDisplay(totalDistance);
    updateSpeedDisplay(0);
    document.getElementById('toggleButton').innerText = "Start Tracking";
    isTracking = false;
}

function updatePosition(position) {
    const { latitude, longitude, speed } = position.coords;

    if (!startPosition) {
        startPosition = { latitude, longitude };
    } else {
        const distance = calculateDistance(startPosition.latitude, startPosition.longitude, latitude, longitude);
        totalDistance += distance;
        startPosition = { latitude, longitude };
    }

    updateDistanceDisplay(totalDistance);
    updateSpeedDisplay(speed);
}

function positionError(error) {
    console.error('Error occurred while tracking:', error.message);
}

function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371e3; // Earth's radius in meters
    const phi1 = (lat1 * Math.PI) / 180;
    const phi2 = (lat2 * Math.PI) / 180;
    const deltaPhi = ((lat2 - lat1) * Math.PI) / 180;
    const deltaLambda = ((lon2 - lon1) * Math.PI) / 180;

    const a = Math.sin(deltaPhi / 2) * Math.sin(deltaPhi / 2) +
        Math.cos(phi1) * Math.cos(phi2) *
        Math.sin(deltaLambda / 2) * Math.sin(deltaLambda / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c;
}

function updateDistanceDisplay(distance) {
    const distanceElement = document.getElementById('distance');
    distanceElement.textContent = distance.toFixed(2) + ' meters';
}

function updateSpeedDisplay(speed) {
    const speedElement = document.getElementById('speed');
    speedElement.textContent = speed.toFixed(2) + ' m/s';
}
