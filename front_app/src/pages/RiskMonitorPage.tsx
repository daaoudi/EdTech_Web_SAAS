// front_app/pages/RiskMonitorPage.tsx

import StudentRiskMonitor from '../components/StudentRiskMonitor';

const RiskMonitorPage = () => {
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto py-8">
        <StudentRiskMonitor />
      </div>
    </div>
  );
};

export default RiskMonitorPage;