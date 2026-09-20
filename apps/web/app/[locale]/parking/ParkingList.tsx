import ParkingCard from "./ParkingCard";
import type { ParkingFacility } from "./parkingApi";

export function ParkingList({ items }: { items: ParkingFacility[] }) {
  return (
    <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 md:gap-6">
      {items.map((facility) => (
        <ParkingCard key={facility.id} facility={facility} />
      ))}
    </div>
  );
}

export default ParkingList;
