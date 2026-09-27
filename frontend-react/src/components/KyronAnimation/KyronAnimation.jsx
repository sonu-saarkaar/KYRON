import { useEffect, useRef, useState } from 'react';
import { FileText, CheckCircle, Zap, Sparkles } from 'lucide-react';

export default function KyronAnimation() {
  const canvasRef = useRef(null);
  const [currentStep, setCurrentStep] = useState(0);

  const animationSteps = [
    { icon: FileText, text: 'Detecting Form', color: 'purple' },
    { icon: Zap, text: 'Filling Fields', color: 'blue' },
    { icon: CheckCircle, text: 'Verifying Data', color: 'green' },
    { icon: Sparkles, text: 'Submitting', color: 'indigo' },
  ];

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    canvas.width = 600;
    canvas.height = 400;

    let animationFrame;
    let time = 0;

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw form background
      ctx.fillStyle = '#f8fafc';
      ctx.fillRect(50, 50, 500, 300);
      ctx.strokeStyle = '#e2e8f0';
      ctx.lineWidth = 2;
      ctx.strokeRect(50, 50, 500, 300);

      // Draw form fields
      const fields = [
        { x: 80, y: 100, width: 200, height: 30, label: 'Name' },
        { x: 300, y: 100, width: 200, height: 30, label: 'Email' },
        { x: 80, y: 150, width: 200, height: 30, label: 'Phone' },
        { x: 300, y: 150, width: 200, height: 30, label: 'Address' },
        { x: 80, y: 200, width: 200, height: 30, label: 'City' },
        { x: 300, y: 200, width: 200, height: 30, label: 'State' },
      ];

      fields.forEach((field, index) => {
        // Field border
        ctx.strokeStyle = '#cbd5e1';
        ctx.lineWidth = 1;
        ctx.strokeRect(field.x, field.y, field.width, field.height);

        // Fill animation based on current step
        if (currentStep >= 1 && index < Math.floor((time / 1000) * 2)) {
          const fillProgress = Math.min(1, (time - index * 500) / 500);
          if (fillProgress > 0 && fillProgress <= 1) {
            ctx.fillStyle = `rgba(99, 102, 241, ${0.3 + fillProgress * 0.4})`;
            ctx.fillRect(field.x, field.y, field.width * fillProgress, field.height);
          }
        }

        // Field label
        ctx.fillStyle = '#64748b';
        ctx.font = '12px Arial';
        ctx.fillText(field.label, field.x + 5, field.y - 5);
      });

      // Draw KYRON cursor/pointer
      if (currentStep >= 1) {
        const cursorX = 80 + ((time % 2000) / 2000) * 420;
        const cursorY = 100 + Math.sin(time / 500) * 100;

        // Cursor circle
        ctx.fillStyle = '#6366f1';
        ctx.beginPath();
        ctx.arc(cursorX, cursorY, 8, 0, Math.PI * 2);
        ctx.fill();

        // Cursor trail
        ctx.strokeStyle = 'rgba(99, 102, 241, 0.3)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(cursorX - 20, cursorY);
        ctx.lineTo(cursorX - 5, cursorY);
        ctx.stroke();
      }

      // Draw success checkmarks
      if (currentStep >= 2) {
        fields.forEach((field, index) => {
          if (index < Math.floor((time / 1000) * 2)) {
            ctx.fillStyle = '#10b981';
            ctx.font = 'bold 16px Arial';
            ctx.fillText('✓', field.x + field.width - 20, field.y + 20);
          }
        });
      }

      time += 16; // ~60fps
      animationFrame = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      if (animationFrame) {
        cancelAnimationFrame(animationFrame);
      }
    };
  }, [currentStep]);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev + 1) % animationSteps.length);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const CurrentIcon = animationSteps[currentStep].icon;

  return (
    <div className="relative w-full h-full flex items-center justify-center">
      {/* Canvas Animation */}
      <div className="relative">
        <canvas
          ref={canvasRef}
          className="rounded-xl shadow-2xl border-2 border-purple-200 dark:border-purple-800"
        />
        
        {/* Overlay with step indicator */}
        <div className="absolute top-4 left-4 flex items-center space-x-2 bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm px-4 py-2 rounded-lg shadow-lg">
          <CurrentIcon className={`w-5 h-5 text-${animationSteps[currentStep].color}-600 dark:text-${animationSteps[currentStep].color}-400`} />
          <span className="text-sm font-semibold text-gray-900 dark:text-white">
            {animationSteps[currentStep].text}
          </span>
        </div>

        {/* KYRON Badge */}
        <div className="absolute bottom-4 right-4 bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-4 py-2 rounded-lg shadow-lg flex items-center space-x-2">
          <Sparkles className="w-4 h-4" />
          <span className="text-sm font-bold">KYRON AI</span>
        </div>
      </div>
    </div>
  );
}

