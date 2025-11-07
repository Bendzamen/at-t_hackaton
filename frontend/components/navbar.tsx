import Image from 'next/image';

const Navbar = () => {
  return (
    <nav className="sticky top-0 z-50 flex items-center gap-2 p-4 bg-white/90 backdrop-blur-md shadow-md">
      <div className="flex items-center">
        <Image src="/logo.png" alt="S Logo" width={32} height={32} />
        <span className="font-bold text-lg text-foreground">lopify</span>
      </div>
    </nav>
  );
};

export default Navbar;
