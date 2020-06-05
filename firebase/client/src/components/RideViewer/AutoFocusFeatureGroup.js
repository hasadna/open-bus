import React, { useEffect, useRef } from "react";
import { FeatureGroup, useLeaflet } from "react-leaflet";

function AutoFocusFeatureGroup(props) {
    const groupRef = useRef(null);

    const context = useLeaflet();
    useEffect(() => {
        context.map.fitBounds(groupRef.current.leafletElement.getBounds());
    });

    return <FeatureGroup ref={groupRef} {...props} />
}

export default AutoFocusFeatureGroup;