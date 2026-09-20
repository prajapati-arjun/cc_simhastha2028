import AccommodationCard from "./AccommodationCard";
import type { Accommodation } from "./accommodationApi";

export function AccommodationList({ items }: { items: Accommodation[] }) {
  return (
    <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 md:gap-6">
      {items.map((item) => (
        <AccommodationCard key={item.id} item={item} />
      ))}
    </div>
  );
}

export default AccommodationList;
