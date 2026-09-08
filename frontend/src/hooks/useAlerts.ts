import { useState, useEffect } from 'react';
import { Alert } from '../types';
import { fetchAlerts } from '../services/api';

export function useAlerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    fetchAlerts().then((data) => {
      if (mounted) {
        setAlerts(data);
        setLoading(false);
      }
    });

    const interval = setInterval(() => {
      fetchAlerts().then((data) => {
        if (mounted) setAlerts(data);
      });
    }, 10000);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  return { alerts, loading, setAlerts };
}
