export default function StatCard({ title, value }) {
  return (
    <div className="
  relative p-6 rounded-xl 
  bg-white/5 backdrop-blur-xl
  border border-cyan-400/20
  shadow-[0_0_25px_rgba(0,255,255,0.15)]
  
  hover:scale-[1.05]
  hover:shadow-[0_0_50px_rgba(0,255,255,0.6)]
  transition duration-300
">
      <h3 className="text-gray-400">{title}</h3>
      <p className="text-3xl font-bold text-cyan-400">{value}</p>
    </div>
  );
}