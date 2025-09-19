declare module "georaster" {
  const parseGeoraster: (arrayBuffer: ArrayBuffer) => Promise<any>;
  export default parseGeoraster;
}
