// logWorker.ts
interface FirewallLog {
    rulenr?: string;
    interface?: string;
    src?: string;
    dst?: string;
    srcport?: string;
    dstport?: string;
    protoname?: string;
    action?: string;
    __timestamp__?: string;
    label?: string;
    digest?: string;
  }
  
  interface LogFilters {
    action: string;
    interface: string;
    direction: string;
  }
  
  self.onmessage = (event) => {
    if (event.data.type === 'processlogs') {
      const { logs, currentLogs, filters, limit } = event.data;
      const processedLogs = processLogs(logs, currentLogs, filters, limit);
      self.postMessage({ type: 'processedlogs', logs: processedLogs });
    }
  };
  
  function processLogs(newLogs: FirewallLog[], currentLogs: FirewallLog[], filters: LogFilters, limit: number): FirewallLog[] {
    let allLogs = [...newLogs, ...currentLogs];
    
    // Apply filters
    allLogs = allLogs.filter(log => {
      return (!filters.action || log.action === filters.action) &&
             (!filters.interface || log.interface === filters.interface) &&
             (!filters.direction || (log.label && log.label.includes(filters.direction)));
    });
  
    // Sort logs by timestamp (newest first)
    allLogs.sort((a, b) => {
      const dateA = a.__timestamp__ ? new Date(a.__timestamp__).getTime() : 0;
      const dateB = b.__timestamp__ ? new Date(b.__timestamp__).getTime() : 0;
      return dateB - dateA;
    });
  
    // Limit the number of logs
    return allLogs.slice(0, limit);
  }