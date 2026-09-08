import { useState, useEffect } from 'react';
import { Camera } from '../types';
import { fetchCameras } from '../services/api';

export function useCameras() {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    fetchCameras().then((data) => {
      if (mounted) {
        setCameras(data);
        setLoading(false);
      }
    });
    return () => {
      mounted = false;
    };
  }, []);

  return { cameras, loading, setCameras };
}
