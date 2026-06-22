import type { NativeStackScreenProps } from "@react-navigation/native-stack";

import type { ProductDetail } from "../api/types";

export type RootStackParamList = {
  Home: undefined;
  Processing: { productId: string };
  TryOn: { product: ProductDetail };
  Calibration: undefined;
};

export type ScreenProps<T extends keyof RootStackParamList> =
  NativeStackScreenProps<RootStackParamList, T>;
