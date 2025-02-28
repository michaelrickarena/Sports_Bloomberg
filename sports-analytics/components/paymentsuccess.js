"use client";

const Success = () => {
  const handleGoHome = () => {
    window.location.href = "/";
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 text-center">
      <div className="bg-white p-10 rounded-lg shadow-lg max-w-md">
        <h1 className="text-3xl font-bold text-green-600 mb-4">
          Payment Successful 🎉
        </h1>
        <p className="text-lg text-gray-700 mb-6">
          Thank you for subscribing to Smart Lines!
        </p>
        <button onClick={handleGoHome} className="payment-success">
          Go to Homepage
        </button>
      </div>
    </div>
  );
};

export default Success;
