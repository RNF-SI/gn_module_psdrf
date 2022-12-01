import {Pipe, PipeTransform} from '@angular/core';


// re-creates the keyvalue pipe for older versions of angular
@Pipe({name: 'keyvalue'})
export class KeyValue implements PipeTransform {
  transform(value: object): Array<object> {
    let vals = [];
    const keys = Object.keys(value).sort();
    for (let i in keys) {
        const key = keys[i];
        vals.push({key: key, value: value[key]})
    }
    return vals;
  }
}


// Formmat a number according to locale
@Pipe({name: 'formatnum'})
export class FormatNum implements PipeTransform {
  transform(value:number): string {
    if (value !== undefined && value !== null) {
      return value.toLocaleString();
    } else {
      return '';
    }
  }
}